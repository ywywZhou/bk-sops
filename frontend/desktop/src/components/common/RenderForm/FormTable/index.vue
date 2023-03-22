<template>
    <div class="form-table">
        <bk-table
            v-if="!tableLoading"
            :data="tableList"
            :pagination="showPagination ? pagination : {}"
            @page-change="handlePageChange">
            <bk-table-column
                v-for="(column, columnIndex) in columnList"
                :key="column.tag_code"
                :label="column.attrs.name"
                :width="column.width"
                :min-width="column.min_width"
                :index="columnIndex"
                show-overflow-tooltip
                :render-header="renderTableHeader"
                :prop="column.tag_code"
                :fixed="column.tag_code === 'tb_btns' ? 'right' : false"
                :align="column.tag_code === 'tb_btns' ? 'center' : 'left'">
                <template slot-scope="{ row, $index }">
                    <template v-if="column.tag_code !== 'tb_btns'">
                        <template v-if="column.children && column.children.length">
                            <bk-table-column
                                v-for="(col, colIndex) in column.children"
                                :key="col.tag_code"
                                :label="col.attrs.name"
                                :width="col.width"
                                :min-width="col.min_width"
                                :index="colIndex"
                                show-overflow-tooltip
                                :render-header="renderTableHeader"
                                :prop="col.tag_code">
                                <template slot-scope="props">
                                    <Cell
                                        ref="tableCell"
                                        :editable="editable"
                                        :index="props.$index"
                                        :row="props.row"
                                        :column="{
                                            ...col,
                                            'index': colIndex
                                        }"
                                        :form-option="formOption"
                                        :pagination="pagination"
                                        @change="handleFormChange">
                                    </Cell>
                                </template>
                            </bk-table-column>
                        </template>
                        <Cell
                            v-else
                            ref="tableCell"
                            :editable="editable"
                            :index="$index"
                            :row="row"
                            :column="{
                                ...column,
                                'index': columnIndex
                            }"
                            :form-option="formOption"
                            :pagination="pagination"
                            @change="handleFormChange">
                        </Cell>
                    </template>
                    <div v-else class="cell-operate">
                        <i
                            v-if="allowAdd"
                            :class="['bk-icon icon-plus-circle-shape add-icon mr15', { 'editable': !editable }]"
                            @click="rowAddClick($index)">
                        </i>
                        <i
                            :class="['bk-icon icon-minus-circle-shape delete-icon', { 'editable': !editable }]"
                            @click="rowDelClick($index)">
                        </i>
                    </div>
                </template>
            </bk-table-column>
            <template v-slot:empty>
                <no-data :style="{ background: 'transparent' }"></no-data>
            </template>
        </bk-table>
    </div>
</template>

<script>
    import tools from '@/utils/tools.js'
    import atomFilter from '@/utils/atomFilter.js'
    import Cell from './Cell.vue'
    import TableHeader from './TableHeader.vue'
    import NoData from '@/components/common/base/NoData.vue'
    export default {
        components: {
            Cell,
            NoData
        },
        props: {
            editable: {
                type: Boolean,
                default: false
            },
            tableLoading: {
                type: Boolean,
                default: false
            },
            value: {
                type: Array,
                default: () => ([])
            },
            showPagination: {
                type: Boolean,
                default: false
            },
            columns: {
                type: Array,
                default: () => ([])
            },
            formOption: {
                type: Object,
                default: () => {
                    return {
                        showGroup: false,
                        showHook: false,
                        showLabel: false,
                        formMode: false
                    }
                }
            },
            allowAdd: {
                type: Boolean,
                default: true
            }
        },
        data () {
            return {
                pagination: {
                    current: 1,
                    count: 0,
                    limit: 10,
                    'show-limit': false
                },
                dataList: tools.deepClone(this.value),
                batchPopoverInstance: null
            }
        },
        computed: {
            tableList () {
                const { current, limit } = this.pagination
                const start = (current - 1) * limit
                return this.dataList.slice(start, start + limit)
            },
            columnList () {
                return this.columns.map(item => {
                    // 频繁使用config里面的参数，解构出来方便使用
                    const { config = {} } = item
                    return {
                        ...item,
                        ...config
                    }
                })
            }
        },
        methods: {
            renderTableHeader (h, { column, $index }) {
                const scheme = this.getScheme(this.columnList, column.property) || {}
                // 如果表格没有数据则禁止批量操作
                const editable = this.tableList.length ? this.editable : false
                return <TableHeader
                    scheme={ scheme }
                    editable={ editable }
                    onTogglePopover={ data => this.onTogglePopover(data) }
                    onUpdate={ data => this.batchUpdate(data, column.property) }>
                </TableHeader>
            },
            getScheme (list, code) {
                let scheme = null
                list.some(item => {
                    if (item.tag_code === code) {
                        scheme = item
                        return true
                    } else if (item.children) {
                        scheme = this.getScheme(item.children, code)
                        return !!scheme
                    }
                })
                return scheme
            },
            onTogglePopover (instance) {
                // 打开新的批量操作气泡时，关掉旧的气泡
                if (this.batchPopoverInstance) {
                    this.batchPopoverInstance.hideHandler()
                }
                this.batchPopoverInstance = instance
            },
            batchUpdate (data, code) {
                // 改数据
                this.tableList.forEach(item => {
                    item[code][code] = data
                })
                // 改状态
                let refs = this.$refs.tableCell
                refs = refs ? Array.from(refs) : []
                refs.forEach(item => {
                    if (item.column.tag_code === code) {
                        console.log(item, code, data)
                        item.isDataChange = data !== item.initRow[code][code]
                        item.validate()
                    }
                })
            },
            rowAddClick (index) {
                const originData = {}
                this.columnList.forEach(item => {
                    let value = ''
                    const { attrs, tag_code } = item
                    if ('value' in attrs) {
                        value = attrs.value
                    } else if ('default' in attrs) {
                        value = attrs.default
                    } else {
                        value = atomFilter.getFormItemDefaultValue([item.config])[tag_code]
                    }
                    originData.new = true
                    originData[tag_code] = {}
                    originData[tag_code][tag_code] = value
                })
                this.dataList.splice(index + 1, 0, originData)
                this.$emit('update', tools.deepClone(this.dataList))
            },
            rowDelClick ($index) {
                const index = (this.pagination.current - 1) * this.pagination.limit + $index
                if (this.tableList.length === 1 && this.pagination.current > 1) {
                    this.pagination.current -= 1
                }
                this.dataList.splice(index, 1)
                this.$emit('update', tools.deepClone(this.dataList))
            },
            handlePageChange (val) {
                this.pagination.current = val
            },
            handleFormChange () {
                this.$emit('update', tools.deepClone(this.dataList))
            },
            validate () {
                const refs = this.$refs.tableCell
                if (!refs) return true
                let valid = true
                Array.from(refs).forEach(item => {
                    const result = item.validate()
                    if (!result) {
                        valid = false
                    }
                })
                return valid
            }
        }
    }
</script>

<style lang="scss">
    .form-table {
        .bk-table {
            .hover-row > td {
                background-color: #fff;
            }
            td, th.is-leaf {
                border-right: 1px solid #dfe0e5;
                &:last-child {
                    border-right: none;
                }
            }
            .sub-header {
                display: flex;
                align-items: center;
            }
            th .cell {
                height: 100%;
                line-height: initial;
            }
            td {
                height: 44px;
                .cell {
                    height: 100%;
                    padding: 0;
                }
                &:first-child .cell-content {
                    left: 0px !important;
                }
            }
            .cell-operate {
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100%;
                .add-icon,
                .delete-icon {
                    font-size: 18px;
                    color: #c4c6cc;
                    cursor: pointer;
                    &:hover {
                        color: #979ba5;
                    }
                    &.disabled {
                        color: #dcdee5;
                        cursor: not-allowed;
                    }
                }
            }
            .bk-table-fixed-right {
                right: 0;
            }
        }
    }
</style>
