"""
Serviço de aplicação para pedidos

Orquestra a criação, conversão de cotações e gestão de pedidos.
Não contém lógica de domínio (fica no domínio), apenas orquestra.
"""

import logging
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.core_engines.delivery_fulfillment import (
    DeliveryFulfillmentImplementation,
    DeliveryFulfillmentPort,
)
from app.core_engines.delivery_fulfillment.dto import (
    DeliveryAddress,
    DeliveryProduct,
    ReadyForDeliveryOrder,
)
from app.core_engines.sales_intelligence import (
    SalesIntelligenceImplementation,
    SalesIntelligencePort,
)
from app.core_engines.sales_intelligence.dto import SaleEvent as SalesSaleEvent
from app.core_engines.sales_intelligence.dto import SoldProduct
from app.core_engines.stock_intelligence import (
    StockIntelligenceImplementation,
    StockIntelligencePort,
)
from app.core_engines.stock_intelligence.dto import SaleEvent, SaleItem
from app.domain.pedido.exceptions import (
    CotacaoNaoAprovadaException,
    CotacaoSemItensException,
    PedidoNaoPodeSerCanceladoException,
)
from app.domain.pedido.validators import calcular_valor_total_item
from app.models.cliente import Cliente
from app.models.cotacao import Cotacao, CotacaoItem
from app.models.obra import Obra
from app.models.pedido import Pedido, PedidoItem
from app.models.produto import Produto
from app.platform.events.publisher import publish_event
from app.platform.events.types import EventType

logger = logging.getLogger(__name__)


class PedidoService:
    """Serviço de aplicação para gestão de pedidos"""

    def __init__(
        self,
        db: Session,
        delivery_fulfillment: DeliveryFulfillmentPort | None = None,
        stock_intelligence: StockIntelligencePort | None = None,
        sales_intelligence: SalesIntelligencePort | None = None,
    ):
        self.db = db
        # Injeção de dependência: usa implementações reais por padrão
        self.delivery_fulfillment = delivery_fulfillment or DeliveryFulfillmentImplementation(db)
        self.stock_intelligence = stock_intelligence or StockIntelligenceImplementation(db)
        self.sales_intelligence = sales_intelligence or SalesIntelligenceImplementation(db)

    def gerar_numero_pedido(self, tenant_id: UUID) -> str:
        """
        Gera número sequencial de pedido para o tenant.

        Formato: PED-001, PED-002, etc.
        """
        ultimo_pedido = (
            self.db.query(Pedido)
            .filter(Pedido.tenant_id == tenant_id)
            .order_by(Pedido.created_at.desc())
            .first()
        )

        if ultimo_pedido and ultimo_pedido.numero:
            try:
                ultimo_numero = int(ultimo_pedido.numero.split("-")[-1])
                novo_numero = ultimo_numero + 1
            except (ValueError, IndexError):
                novo_numero = 1
        else:
            novo_numero = 1

        return f"PED-{novo_numero:03d}"

    def criar_pedido(
        self,
        tenant_id: UUID,
        cliente_id: UUID,
        usuario_id: UUID,
        itens: list,
        obra_id: UUID | None = None,
        cotacao_id: UUID | None = None,
        desconto_percentual: Decimal = Decimal("0"),
        observacoes: str | None = None,
    ) -> Pedido:
        """
        Cria novo pedido diretamente (sem cotação).

        Validações:
        - Cliente deve existir
        - Obra deve existir e pertencer ao cliente (se fornecida)
        - Produtos devem existir e estar ativos
        - Deve ter pelo menos 1 item
        """
        # Valida cliente
        cliente = (
            self.db.query(Cliente)
            .filter(Cliente.id == cliente_id, Cliente.tenant_id == tenant_id)
            .first()
        )

        if not cliente:
            raise ValueError("Cliente não encontrado")

        # Valida obra se fornecida
        if obra_id:
            obra = (
                self.db.query(Obra)
                .filter(
                    Obra.id == obra_id, Obra.tenant_id == tenant_id, Obra.cliente_id == cliente_id
                )
                .first()
            )

            if not obra:
                raise ValueError("Obra não encontrada ou não pertence ao cliente")

        # Valida produtos e cria itens
        pedido_itens = []
        for idx, item_data in enumerate(itens):
            produto = (
                self.db.query(Produto)
                .filter(
                    Produto.id == item_data["produto_id"],
                    Produto.tenant_id == tenant_id,
                    Produto.ativo is True,
                )
                .first()
            )

            if not produto:
                raise ValueError(f"Produto {item_data['produto_id']} não encontrado ou inativo")

            # Usa preço do produto se não fornecido ou se fornecido mas é 0
            preco_unitario_fornecido = item_data.get("preco_unitario")
            if preco_unitario_fornecido is None or preco_unitario_fornecido == 0:
                preco_unitario = produto.preco_base
            else:
                preco_unitario = preco_unitario_fornecido
            desconto_item = item_data.get("desconto_percentual", Decimal("0"))

            valor_total = calcular_valor_total_item(
                item_data["quantidade"], preco_unitario, desconto_item
            )

            pedido_itens.append(
                {
                    "produto": produto,
                    "quantidade": item_data["quantidade"],
                    "preco_unitario": preco_unitario,
                    "desconto_percentual": desconto_item,
                    "valor_total": valor_total,
                    "observacoes": item_data.get("observacoes"),
                    "ordem": item_data.get("ordem", idx),
                }
            )

        if not pedido_itens:
            raise ValueError("Pedido deve ter pelo menos um item")

        # Cria pedido
        numero = self.gerar_numero_pedido(tenant_id)

        pedido = Pedido(
            tenant_id=tenant_id,
            cotacao_id=cotacao_id,
            cliente_id=cliente_id,
            obra_id=obra_id,
            numero=numero,
            status="pendente",
            desconto_percentual=desconto_percentual,
            observacoes=observacoes,
            usuario_id=usuario_id,
        )

        self.db.add(pedido)
        self.db.flush()

        # Cria itens
        for item_data in pedido_itens:
            item = PedidoItem(
                tenant_id=tenant_id,
                pedido_id=pedido.id,
                produto_id=item_data["produto"].id,
                quantidade=item_data["quantidade"],
                preco_unitario=item_data["preco_unitario"],
                desconto_percentual=item_data["desconto_percentual"],
                valor_total=item_data["valor_total"],
                observacoes=item_data["observacoes"],
                ordem=item_data["ordem"],
            )
            self.db.add(item)

        self.db.commit()
        self.db.refresh(pedido)

        return pedido

    def converter_cotacao_em_pedido(
        self,
        cotacao_id: UUID,
        tenant_id: UUID,
        usuario_id: UUID,
    ) -> Pedido:
        """
        Converte cotação aprovada em pedido (1 clique).

        Esta é a funcionalidade principal do MVP 1.

        Endpoint IDEMPOTENTE: Se a cotação já foi convertida, retorna o pedido existente.
        Operação TRANSACIONAL com lock pessimista para evitar condições de corrida.

        Validações:
        - Cotação deve existir
        - Cotação deve estar aprovada
        - Cotação deve ter pelo menos 1 item

        Processo:
        1. Busca cotação com lock pessimista (com proteção contra concorrência)
        2. Verifica se já foi convertida (idempotência)
        3. Valida status (deve estar aprovada)
        4. Cria pedido copiando dados da cotação (transacional)
        5. Copia todos os itens da cotação para o pedido (preços "congelados")
        6. Atualiza cotação para status "convertida"
        """
        # Busca cotação com LOCK PESSIMISTA (proteção contra concorrência)
        # with_for_update() garante que apenas uma transação pode ler/modificar
        # Isso evita condições de corrida quando múltiplas requisições tentam converter
        cotacao = (
            self.db.query(Cotacao)
            .filter(Cotacao.id == cotacao_id, Cotacao.tenant_id == tenant_id)
            .with_for_update()
            .first()
        )

        if not cotacao:
            raise ValueError("Cotação não encontrada")

        # IDEMPOTÊNCIA: Se já foi convertida, retorna o pedido existente
        pedido_existente = (
            self.db.query(Pedido)
            .filter(Pedido.cotacao_id == cotacao_id, Pedido.tenant_id == tenant_id)
            .first()
        )

        if pedido_existente:
            # Retorna pedido existente (idempotência)
            return pedido_existente

        # Validações de domínio (só valida se não foi convertida ainda)
        if cotacao.status != "aprovada":
            raise CotacaoNaoAprovadaException(
                "Apenas cotações aprovadas podem ser convertidas em pedido"
            )

        # Busca itens da cotação (com tenant_id garantido)
        cotacao_itens = (
            self.db.query(CotacaoItem)
            .filter(CotacaoItem.cotacao_id == cotacao_id, CotacaoItem.tenant_id == tenant_id)
            .order_by(CotacaoItem.ordem)
            .all()
        )

        if not cotacao_itens:
            raise CotacaoSemItensException("Cotação não possui itens")

        # OPERAÇÃO TRANSACIONAL: Tudo ou nada
        try:
            # Cria pedido copiando dados da cotação
            numero = self.gerar_numero_pedido(tenant_id)

            pedido = Pedido(
                tenant_id=tenant_id,
                cotacao_id=cotacao.id,
                cliente_id=cotacao.cliente_id,
                obra_id=cotacao.obra_id,
                numero=numero,
                status="pendente",
                desconto_percentual=cotacao.desconto_percentual,
                observacoes=cotacao.observacoes,
                usuario_id=usuario_id,
            )

            self.db.add(pedido)
            self.db.flush()

            # Copia itens da cotação para o pedido (preços "congelados")
            for idx, cotacao_item in enumerate(cotacao_itens):
                pedido_item = PedidoItem(
                    tenant_id=tenant_id,
                    pedido_id=pedido.id,
                    produto_id=cotacao_item.produto_id,
                    quantidade=cotacao_item.quantidade,
                    preco_unitario=cotacao_item.preco_unitario,  # Preço "congelado"
                    desconto_percentual=cotacao_item.desconto_percentual,
                    valor_total=cotacao_item.valor_total,  # Valor "congelado"
                    observacoes=cotacao_item.observacoes,
                    ordem=cotacao_item.ordem if cotacao_item.ordem > 0 else idx,
                )
                self.db.add(pedido_item)

            # Atualiza status da cotação
            cotacao.status = "convertida"
            cotacao.convertida_em = datetime.utcnow()

            # PUBLICAR EVENTO: quote_converted (na mesma transação ANTES do commit)
            try:
                publish_event(
                    db=self.db,
                    event_type=EventType.QUOTE_CONVERTED,
                    tenant_id=tenant_id,
                    payload={
                        "quote_id": str(cotacao.id),
                        "order_id": str(pedido.id),
                        "client_id": str(cotacao.cliente_id),
                        "user_id": str(usuario_id),
                        "work_id": str(pedido.obra_id) if pedido.obra_id else None,
                        "total_value": str(sum(item.valor_total for item in pedido.itens)),
                        "converted_at": datetime.utcnow().isoformat(),
                        "items": [
                            {
                                "product_id": str(item.produto_id),
                                "quantity": str(item.quantidade),
                                "unit_price": str(item.preco_unitario),
                                "total_value": str(item.valor_total),
                            }
                            for item in pedido.itens
                        ],
                    },
                    version="1.0",
                )
            except Exception as e:
                # Fail gracefully: se publicação de evento falhar, loga mas não quebra transação
                logger.warning(
                    "Falha ao publicar evento quote_converted",
                    extra={
                        "tenant_id": str(tenant_id),
                        "quote_id": str(cotacao.id),
                        "order_id": str(pedido.id),
                        "error": str(e),
                    },
                    exc_info=True,
                )
                # NÃO levanta exceção - permite que transação continue

            # COMMIT TRANSACIONAL: Tudo ou nada (pedido + evento)
            self.db.commit()
            self.db.refresh(pedido)

            # Sales Intelligence Engine: Registra venda concluída para atualizar histórico de vendas
            # MANTIDO para compatibilidade (será removido quando handlers estiverem prontos)
            try:
                produtos_vendidos = [
                    SoldProduct(
                        produto_id=item.produto_id,
                        quantidade=item.quantidade,
                        preco_unitario=item.preco_unitario,
                        valor_total=item.valor_total,
                        foi_sugerido=False,  # MVP2: pode ser melhorado com tracking de sugestões
                    )
                    for item in pedido.itens
                ]
                sale_event = SalesSaleEvent(
                    tenant_id=tenant_id,
                    pedido_id=pedido.id,
                    produtos_vendidos=produtos_vendidos,
                    valor_total_pedido=sum(item.valor_total for item in pedido.itens),
                    cotacao_id=cotacao.id,
                    cliente_id=cotacao.cliente_id,
                    data_venda=datetime.utcnow(),
                )
                self.sales_intelligence.register_sale(sale_event)
            except Exception as e:
                # Fail gracefully: se engine não disponível, continua normalmente
                logger.warning(
                    "Falha ao registrar venda no Sales Intelligence Engine",
                    extra={
                        "tenant_id": str(tenant_id),
                        "pedido_id": str(pedido.id),
                        "cotacao_id": str(cotacao.id),
                        "error": str(e),
                    },
                    exc_info=True,
                )

            return pedido

        except Exception:
            # ROLLBACK em caso de erro
            self.db.rollback()
            raise

    def cancelar_pedido(self, pedido_id: UUID, tenant_id: UUID) -> Pedido:
        """
        Cancela pedido.

        Validações:
        - Pedido deve existir
        - Pedido não pode estar entregue
        """
        pedido = (
            self.db.query(Pedido)
            .filter(Pedido.id == pedido_id, Pedido.tenant_id == tenant_id)
            .first()
        )

        if not pedido:
            raise ValueError("Pedido não encontrado")

        if pedido.status == "entregue":
            raise PedidoNaoPodeSerCanceladoException("Não é possível cancelar pedido já entregue")

        pedido.status = "cancelado"

        self.db.commit()
        self.db.refresh(pedido)

        return pedido

    def atualizar_status_pedido(
        self,
        pedido_id: UUID,
        tenant_id: UUID,
        novo_status: str,
        usuario_id: UUID | None = None,
    ) -> Pedido:
        """
        Atualiza status do pedido.

        Validações:
        - Pedido deve existir
        - Status deve ser válido
        """
        pedido = (
            self.db.query(Pedido)
            .filter(Pedido.id == pedido_id, Pedido.tenant_id == tenant_id)
            .first()
        )

        if not pedido:
            raise ValueError("Pedido não encontrado")

        status_validos = ["pendente", "em_preparacao", "saiu_entrega", "entregue", "cancelado"]
        if novo_status not in status_validos:
            raise ValueError(f"Status inválido: {novo_status}")

        # Salva status antigo antes de atualizar
        status_antigo = pedido.status

        # Se status for "entregue", registra data de entrega
        if novo_status == "entregue":
            pedido.entregue_em = datetime.utcnow()

            # PUBLICAR EVENTO: sale_recorded (na mesma transação)
            try:
                publish_event(
                    db=self.db,
                    event_type=EventType.SALE_RECORDED,
                    tenant_id=tenant_id,
                    payload={
                        "order_id": str(pedido_id),
                        "quote_id": str(pedido.cotacao_id) if pedido.cotacao_id else None,
                        "client_id": str(pedido.cliente_id),
                        "work_id": str(pedido.obra_id) if pedido.obra_id else None,
                        "delivered_at": pedido.entregue_em.isoformat(),
                        "total_value": str(sum(item.valor_total for item in pedido.itens)),
                        "items": [
                            {
                                "product_id": str(item.produto_id),
                                "quantity": str(item.quantidade),
                                "unit_price": str(item.preco_unitario),
                                "total_value": str(item.valor_total),
                            }
                            for item in pedido.itens
                        ],
                    },
                    version="1.0",
                )
            except Exception as e:
                # Fail gracefully: se publicação de evento falhar, loga mas não quebra transação
                logger.warning(
                    "Falha ao publicar evento sale_recorded",
                    extra={
                        "tenant_id": str(tenant_id),
                        "pedido_id": str(pedido_id),
                        "error": str(e),
                    },
                    exc_info=True,
                )
                # NÃO levanta exceção - permite que transação continue

            # COMMIT: sale_recorded evento na mesma transação
            self.db.commit()
            self.db.refresh(pedido)

            # Stock Intelligence Engine: Registra venda (pedido entregue = venda concluída) para atualizar histórico
            # MANTIDO para compatibilidade (será removido quando handlers estiverem prontos)
            try:
                itens = [
                    SaleItem(
                        produto_id=item.produto_id,
                        quantidade=item.quantidade,
                        valor_total=item.valor_total,
                    )
                    for item in pedido.itens
                ]
                sale_event = SaleEvent(
                    tenant_id=tenant_id,
                    pedido_id=pedido_id,
                    data_entrega=pedido.entregue_em,
                    itens=itens,
                )
                self.stock_intelligence.register_sale(sale_event)
            except Exception as e:
                # Fail gracefully: se engine não disponível, continua normalmente
                logger.warning(
                    "Falha ao registrar venda no Stock Intelligence Engine",
                    extra={
                        "tenant_id": str(tenant_id),
                        "pedido_id": str(pedido_id),
                        "error": str(e),
                    },
                    exc_info=True,
                )

        # PUBLICAR EVENTO: order_status_changed (na mesma transação ANTES do commit)
        try:
            publish_event(
                db=self.db,
                event_type=EventType.ORDER_STATUS_CHANGED,
                tenant_id=tenant_id,
                payload={
                    "order_id": str(pedido_id),
                    "old_status": status_antigo,
                    "new_status": novo_status,
                    "changed_at": datetime.utcnow().isoformat(),
                    "changed_by": str(usuario_id) if usuario_id else None,
                },
                version="1.0",
            )
        except Exception as e:
            # Fail gracefully: se publicação de evento falhar, loga mas não quebra transação
            logger.warning(
                "Falha ao publicar evento order_status_changed",
                extra={"tenant_id": str(tenant_id), "pedido_id": str(pedido_id), "error": str(e)},
                exc_info=True,
            )
            # NÃO levanta exceção - permite que transação continue

        # Atualiza status do pedido ANTES do commit
        pedido.status = novo_status

        # COMMIT: status + eventos na mesma transação
        self.db.commit()
        self.db.refresh(pedido)

        # Delivery & Fulfillment Engine: Se status for "saiu_entrega", consulta engine para planejar rotas
        # MANTIDO para compatibilidade (será removido quando handlers estiverem prontos)
        # O evento order_status_changed já foi publicado e será processado pelo handler
        if novo_status == "saiu_entrega":
            try:
                # Busca endereço de entrega (do cliente ou da obra)
                endereco = self._get_delivery_address(pedido)

                # Converte itens para DeliveryProduct
                produtos = [
                    DeliveryProduct(
                        produto_id=item.produto_id,
                        quantidade=item.quantidade,
                        peso=None,  # Futuro: peso do produto
                        volume=None,  # Futuro: volume do produto
                    )
                    for item in pedido.itens
                ]

                order = ReadyForDeliveryOrder(
                    tenant_id=tenant_id,
                    pedido_id=pedido_id,
                    cliente_id=pedido.cliente_id,
                    endereco_entrega=endereco,
                    produtos=produtos,
                    obra_id=pedido.obra_id,
                    prioridade="normal",
                    observacoes=pedido.observacoes,
                )
                _rotas = self.delivery_fulfillment.plan_routes([order])
                # TODO: Vertical decide como usar rotas sugeridas (pode ser retornado via API)
            except Exception as e:
                # Fail gracefully: se engine não disponível, continua normalmente
                logger.warning(
                    "Falha ao planejar rotas no Delivery & Fulfillment Engine",
                    extra={
                        "tenant_id": str(tenant_id),
                        "pedido_id": str(pedido_id),
                        "error": str(e),
                    },
                    exc_info=True,
                )

        pedido.status = novo_status

        self.db.commit()
        self.db.refresh(pedido)

        return pedido

    def _get_delivery_address(self, pedido: Pedido) -> DeliveryAddress:
        """
        Método auxiliar para obter endereço de entrega.
        Prioriza endereço da obra, depois endereço do cliente.
        """
        from app.models.cliente import Cliente
        from app.models.obra import Obra

        # Se tem obra, usa endereço da obra
        if pedido.obra_id:
            obra = self.db.query(Obra).filter(Obra.id == pedido.obra_id).first()
            if obra and obra.endereco:
                # Parse endereço da obra (formato simples: "Rua, Número - Bairro")
                endereco_parts = obra.endereco.split(",") if obra.endereco else []
                rua_numero = (
                    endereco_parts[0].strip() if len(endereco_parts) > 0 else obra.endereco or ""
                )
                bairro = endereco_parts[1].strip() if len(endereco_parts) > 1 else ""

                # Separa rua e número
                rua_numero_parts = rua_numero.split("-")
                rua = rua_numero_parts[0].strip() if len(rua_numero_parts) > 0 else rua_numero
                numero = rua_numero_parts[1].strip() if len(rua_numero_parts) > 1 else ""

                return DeliveryAddress(
                    rua=rua,
                    numero=numero,
                    bairro=bairro,
                    cidade=obra.cidade or "",
                    estado=obra.estado or "",
                    cep="",
                    coordenadas_gps=None,
                    instrucoes_acesso=None,
                    horario_preferencial=None,
                )

        # Usa endereço do cliente
        cliente = self.db.query(Cliente).filter(Cliente.id == pedido.cliente_id).first()
        if cliente and cliente.endereco:
            # Parse endereço do cliente (formato simples)
            endereco_parts = cliente.endereco.split(",") if cliente.endereco else []
            rua_numero = (
                endereco_parts[0].strip() if len(endereco_parts) > 0 else cliente.endereco or ""
            )
            bairro = endereco_parts[1].strip() if len(endereco_parts) > 1 else ""

            # Separa rua e número
            rua_numero_parts = rua_numero.split("-")
            rua = rua_numero_parts[0].strip() if len(rua_numero_parts) > 0 else rua_numero
            numero = rua_numero_parts[1].strip() if len(rua_numero_parts) > 1 else ""

            return DeliveryAddress(
                rua=rua,
                numero=numero,
                bairro=bairro,
                cidade=cliente.cidade or "",
                estado=cliente.estado or "",
                cep=cliente.cep or "",
                coordenadas_gps=None,
                instrucoes_acesso=None,
                horario_preferencial=None,
            )

        # Fallback: endereço vazio
        return DeliveryAddress(
            rua="",
            numero="",
            bairro="",
            cidade="",
            estado="",
            cep="",
            coordenadas_gps=None,
            instrucoes_acesso=None,
            horario_preferencial=None,
        )
