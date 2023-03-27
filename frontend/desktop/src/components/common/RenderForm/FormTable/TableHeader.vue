<template>
    <div class="render-table-header">
        <p v-bk-overflow-tips class="label-text" v-if="scheme.attrs?.name">
            {{ scheme.attrs.name }}
        </p>
        <!--如果存在二级表头, 批量编辑放在二级表头, 否则放在一级表头-->
        <bk-popover
            v-if="editable && !scheme.children && scheme.batch_edit"
            ref="batchUpdatePopover"
            placement="bottom"
            theme="light"
            :arrow="false"
            trigger="manual"
            offset="0,13px"
            width="250"
            :tippy-options="{ hideOnClick: false }"
            class="batch-operate-tippy"
            ext-cls="batch-operate-tippy-popper">
            <i class="bk-icon icon-edit" :class="{ 'active': batchPopoverInstance }" @click="showPopover"></i>
            <template slot="content">
                <div class="batch-edit-title">{{ $t('批量编辑') + scheme.attrs.name }}</div>
                <div class="batch-edit-content">
                    <TagSelect
                        v-if="scheme.type === 'select'"
                        v-bind="getDefaultAttrs()"
                        :tag-code="scheme.tag_code"
                        :atom-events="scheme.events"
                        :atom-methods="scheme.methods"
                        :value="formValue"
                        @change="selectChange">
                    </TagSelect>
                    <bk-input
                        v-else
                        :clearable="true"
                        v-model="formValue">
                    </bk-input>
                </div>
                <div class="batch-edit-footer">
                    <bk-button text ext-cls="footer-confirm" @click="handleBatchConfirm">
                        {{ $t('确定') }}
                    </bk-button>
                    <bk-button text ext-cls="footer-cancel" class="ml20" @click="hidePopover">
                        {{ $t('取消') }}
                    </bk-button>
                </div>
            </template>
        </bk-popover>
    </div>
</template>

<script>
    import tools from '@/utils/tools.js'
    import TagSelect from '../tags/TagSelect.vue'
    export default {
        components: {
            TagSelect
        },
        props: {
            scheme: {
                type: Object,
                default: () => ({})
            },
            editable: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                formValue: '',
                batchPopoverInstance: null
            }
        },
        methods: {
            getDefaultAttrs () {
                const attrs = tools.deepClone(this.scheme.attrs)
                attrs.formEdit = true
                attrs.formMode = true

                return { ...attrs }
            },
            showPopover () {
                this.batchPopoverInstance = this.$refs['batchUpdatePopover']
                this.$emit('togglePopover', this.batchPopoverInstance)
                this.batchPopoverInstance.showHandler()
            },
            hidePopover () {
                this.formValue = ''
                this.$emit('togglePopover', null)
            },
            selectChange (fieldArr, val) {
                this.formValue = val
            },
            handleBatchConfirm () {
                this.$emit('update', this.formValue)
                this.hidePopover()
            }
        }
    }
</script>

<style lang="scss" scoped>
    .render-table-header {
        display: flex;
        align-items: center;
        .icon-edit {
            margin-left: 6px;
            color: #979ba5;
            cursor: pointer;
            &.active {
                color: #3a84ff;
            }
        }
    }
</style>
<style lang="scss">
    .batch-operate-tippy-popper {
        .tippy-tooltip {
            padding: 0;
            border: 1px solid #dcdee5;
            border-radius: 0;
            box-shadow: none;
            transform: none !important;
        }
        .batch-edit-title {
            font-size: 14px;
            color: #63656E;
            padding: 10px 15px;
        }
        .batch-edit-content {
            padding: 0 15px 14px 15px;
            .el-select {
                .el-input__inner {
                    border-color: #c4c6cc;
                    border-radius: 0 !important;
                }
                .el-input__icon {
                    color: #979ba5;
                }
                .is-focus .el-input__inner{
                    border-color: #3a84ff;
                }
            }
        }
        .batch-edit-footer {
            display: flex;
            align-items: center;
            justify-content: flex-end;
            flex-basis: 32px;
            padding: 5px 15px;
            border-top: 1px solid #F0F1F5;
            font-size: 12px;
        }
    }
</style>
