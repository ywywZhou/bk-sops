<template>
    <div class="cell-wrapper">
        <div
            :class="['cell-content', {
                'disabled': !editable,
                'valid-error': !validateInfo.valid,
                'active': isActive,
                'change-cell': isDataChange,
                'add-cell': row.new
            }]"
            v-bk-overflow-tips
            @click="onCellClick">
            {{ getFormTextValue() || '--' }}
            <div class="icon-wrap" v-if="editable">
                <i
                    v-if="!validateInfo.valid"
                    v-bk-tooltips="validateInfo.message"
                    class="common-icon-dark-circle-warning">
                </i>
                <i
                    v-else-if="getFormTextValue()"
                    class="common-icon-dark-circle-close">
                </i>
            </div>
        </div>
        <!-- 参数被使用占位popover -->
        <bk-popover
            v-if="isActive"
            ref="cellComponentPopover"
            placement="top-start"
            theme="light"
            always
            :width="`${column.width + (column.index === 0 ? 0 : 1)}`"
            :arrow="false"
            :offset="`${column.index === 0 ? 0 : -1},-13px`"
            :duration="0"
            class="cell-component-tippy"
            ext-cls="cell-component-tippy-popper">
            <div class="empty-box"></div>
            <template slot="content">
                <render-form
                    class="cell-component"
                    :ref="`row_${(pagination.current - 1) * pagination.limit + index}_${column.tag_code}`"
                    :scheme="getScheme()"
                    :form-option="getCellOption((pagination.current - 1) * pagination.limit + index)"
                    v-bk-clickoutside="handleClickOutside"
                    v-model="row[column.tag_code]">
                </render-form>
            </template>
        </bk-popover>
    </div>
</template>

<script>
    import tools from '@/utils/tools.js'
    import dom from '@/utils/dom.js'
    import { checkDataType } from '@/utils/checkDataType.js'
    import RenderForm from '../RenderForm.vue'
    export default {
        components: {
            RenderForm
        },
        props: {
            editable: {
                type: Boolean,
                default: false
            },
            column: {
                type: Object,
                default: () => ({})
            },
            row: {
                type: Object,
                default: () => ({})
            },
            index: {
                type: Number,
                default: 0
            },
            pagination: {
                type: Object,
                default: () => {
                    return {
                        current: 1,
                        count: 0,
                        limit: 10
                    }
                }
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
            }
        },
        data () {
            return {
                initRow: tools.deepClone(this.row),
                curFormItemRef: null,
                isActive: false,
                validateInfo: {
                    valid: true,
                    message: ''
                },
                isDataChange: false,
                tableScroller: null
            }
        },
        computed: {

        },
        mounted () {
            
        },
        beforeDestroy () {
            this.tableScroller && this.tableScroller.removeEventListener('scroll', this.handleTableScroll)
        },
        methods: {
            // 获取表格数据展示文本
            getFormTextValue () {
                const { tag_code, type, attrs } = this.column
                const value = this.row[tag_code]
                /** warning 前端tag结构变化数据兼容 */
                if (tag_code === 'job_task') {
                    return this.reloadValue(value)
                } else if (type === 'textarea') {
                    return value[tag_code].split('\n').filter(item => item.trim()).join(',')
                } else if (type === 'upload') {
                    return this.$t('上传文件')
                } else if (type === 'select' && attrs.items?.length) {
                    // 避免展示出选项中的value
                    const isExist = attrs.items.some(item => item.text === value[tag_code])
                    if (isExist) return value[tag_code]
                    const matchInfo = attrs.items.find(item => item.value === value[tag_code])
                    if (matchInfo) {
                        return matchInfo.text
                    }
                }
                return value[tag_code]
            },
            /**
             * 表单参数重载
             * 前端tag结构变化数据兼容
             */
            reloadValue (rawData) {
                if (typeof this.column.reloadValue === 'function') {
                    const reloadValue = this.column.reloadValue(rawData)
                    if (reloadValue) {
                        return reloadValue[this.column.tag_code]
                    }
                }
                return rawData[this.column.tag_code]
            },
            // 表单设置
            getScheme () {
                // 标识是编辑式表格
                if (this.column.attrs) {
                    this.column.attrs.formTable = true
                }
                return [this.column]
            },
            // 单元格内的renderform表单属性配置
            getCellOption (index) {
                const options = Object.assign({}, this.formOption)
                options.formMode = true

                return options
            },
            // 是否显示编辑态
            onCellClick () {
                if (!this.editable) return
                this.isActive = true
                // 自动聚焦
                const { current, limit } = this.pagination
                const refName = `row_${(current - 1) * limit + this.index}_${this.column.tag_code}`
                setTimeout(() => {
                    const formRef = this.$refs[refName]
                    const formItemRef = formRef && formRef.$children[0]
                    formItemRef && formItemRef.onFocusForm()
                    this.curFormItemRef = formItemRef
                    // 监听表格滚动
                    if (!this.tableScroller) {
                        this.tableScroller = document.querySelector('.form-table .bk-table-body-wrapper')
                    }
                    this.tableScroller && this.tableScroller.addEventListener('scroll', this.handleTableScroll, { passive: true })
                }, 200)
            },
            // 点击单元格外面, 关闭表单项
            handleClickOutside (mousedownEvent, mouseupEvent) {
                if (dom.parentClsContains('tag-component-popper', mouseupEvent.target)) {
                    return
                }
                // 根据表单值进行判断
                if (this.curFormItemRef) {
                    // 获取表单项校验
                    this.validateInfo = this.curFormItemRef.getValidateInfo()
                    // 单元格数据是否和初始时一致
                    const value = this.curFormItemRef.value
                    const { tag_code } = this.column
                    this.isDataChange = value !== this.initRow[tag_code][tag_code]
                }
            
                this.$emit('change')
                this.isActive = false
                this.curFormItemRef = null
                // 销毁表格滚动监听
                this.tableScroller && this.tableScroller.removeEventListener('scroll', this.handleTableScroll)
            },
            // 处理表格滚动，滚动时清除当前选中的表单项，否则会跟随表格滚动
            handleTableScroll () {
                this.isActive = false
                this.curFormItemRef = null
            },
            validate () {
                const { attrs, tag_code } = this.column
                if (!attrs.validation) return true

                const isValid = attrs.validation.every((item) => {
                    const value = this.row[tag_code][tag_code]
                    const result = this.getValidateResult(item, value)
                    this.validateInfo = result
                    return result.valid
                })
                return isValid
            },
            /**
             * 通用校验规则
             * @param {Object} config tag 配置项
             * @param {Any} value tag 值
             * @param {Object} parentValue 父组件值
             *
             * @returns {Object} 校验结果和提示信息
             */
            getValidateResult (config, value, parentValue = '') {
                let valid = true
                let message = ''
                const validateSet = ['required', 'custom', 'regex']
                if (validateSet.includes(config.type)) {
                    switch (config.type) {
                        case 'required': {
                            const valueType = checkDataType(value)
                            let valueEmpty = false
                            if (valueType === 'Object') {
                                valueEmpty = !Object.keys(value).length
                            } else if (valueType === 'String' || valueType === 'Array') {
                                valueEmpty = !value.length
                            } else if (valueType === 'Number') {
                                valueEmpty = !value.toString()
                            }
                            if (valueEmpty) {
                                valid = false
                                message = this.$t('必填项')
                            }
                            break
                        }
                        case 'regex':
                            if (!/^\${[^${}]+}$/.test(value)) {
                                const reg = new RegExp(config.args)
                                if (!reg.test(value)) {
                                    valid = false
                                    message = config.error_message
                                }
                            }
                            break
                        case 'custom':
                            if (!/^\${[^${}]+}$/.test(value)) {
                                const validateInfo = config.args.call(this, value, parentValue)
                                if (!validateInfo.result) {
                                    valid = false
                                    message = validateInfo.error_message
                                }
                            }
                            break
                        default:
                            break
                    }
                }

                return { valid, message }
            }
        }
    }
</script>

<style lang="scss">
    .cell-wrapper {
        .cell-content {
            position: absolute;
            left: -1px;
            right: -1px;
            bottom: -1px;
            height: 44px;
            line-height: 42px;
            border: 1px solid transparent;
            padding: 0 10px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            cursor: pointer;
            .icon-wrap {
                position: absolute;
                right: 10px;
                top: 14px;
                font-size: 16px;
                .common-icon-dark-circle-warning {
                    display: block;
                    color: #ea3636;
                }
                .common-icon-dark-circle-close {
                    display: none;
                    color: #c4c6cc;
                    &:hover {
                        color: #979ba5;
                    }
                }
            }
            &:hover {
                border-color:#699df4;
                .common-icon-dark-circle-close {
                    display: block;
                }
            }
            &.active {
                border-color:#699df4;
            }
            &.disabled {
                background-color: #fafbfd;
                cursor: not-allowed;
            }
            &.change-cell {
                background: #fff3e1;
                border-color: #dfe0e5;
            }
            &.add-cell {
                background: #f2fff4;
                border-color: #dfe0e5;
            }
            &.valid-error {
                background: #fff0f0;
                border-color: #dfe0e5;
            }
        }
        .cell-component-tippy,
        .bk-tooltip-ref,
        .empty-box {
            height: 100%;
            width: 100%;
        }
    }
</style>

<style lang="scss">
    .cell-component-tippy-popper {
        padding: 0;
        border: none;
        .tippy-tooltip {
            padding: 0;
            transform: none !important;
            border-radius: 0;
            box-shadow: none;
        }
        .render-form .rf-tag-form {
            .el-input__inner,
            .el-textarea__inner {
                border-color: #3a84ff;
                border-radius: 0 !important;
            }
            .el-input__inner {
                height: 44px;
                line-height: 42px;
            }
        }
    }
    .tag-component-popper {
        margin-top: 4px !important;
        border-color: #dcdee5;
        border-radius: 0;
        .el-select-dropdown__item {
            color: #63656e;
            padding: 0 16px;
            &.selected {
                font-weight: normal;
                color: #3a84ff;
                background-color: #f4f6fa;
            }
            &:hover {
                background-color: #eaf3ff;
            }
        }
        .popper__arrow {
            display: none;
        }
    }
</style>
