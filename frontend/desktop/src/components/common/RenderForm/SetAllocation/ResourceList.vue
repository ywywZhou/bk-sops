/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
<template>
    <div class="resource-list">
        <div class="opt-btns" v-if="!viewValue">
            <bk-button
                theme="default"
                size="small"
                :disabled="!editable"
                @click="$emit('update:showFilter', true)">
                {{ i18n.resourceFilter }}
            </bk-button>
            <bk-button
                theme="default"
                size="small"
                :disabled="!editable"
                @click="exportData">
                {{ i18n.export }}
            </bk-button>
            <el-upload
                ref="upload"
                class="upload-btn"
                action="/"
                :disabled="!editable"
                :show-file-list="false"
                :on-change="importData"
                :auto-upload="false">
                <bk-button
                    slot="trigger"
                    size="small"
                    :disabled="!editable"
                    theme="default">
                    {{ i18n.import }}
                </bk-button>
            </el-upload>
        </div>
        <bk-alert v-if="hasDiff" :class="{ 'alert-disabled': !editable }" ref="diffAlert" type="warning" style="margin-bottom: 10px;" :show-icon="false">
            <div class="diff-alert" slot="title">
                <span>{{ $t('变量保存数据与最新的CMDB集群配置存在差异，是否更新变量数据？') }}</span>
                <bk-link theme="primary" @click="updateDiffData">{{ $t('确认') }}</bk-link>
            </div>
        </bk-alert>
        <FormTable
            ref="tableForm"
            :editable="editable"
            :value="tableData"
            :columns="cols"
            :allow-add="false"
            @update="$emit('update', $event)">
        </FormTable>
        <separator-select :editable="editable" :value="separator" @change="$emit('update:separator', $event)"></separator-select>
    </div>
</template>
<script >
    import '@/utils/i18n.js'
    import XLSX from 'xlsx'
    import tools from '@/utils/tools.js'
    import SeparatorSelect from '../SeparatorSelect.vue'
    import FormTable from '../FormTable/index.vue'

    export default {
        name: 'ResourceList',
        components: {
            SeparatorSelect,
            FormTable
        },
        props: {
            loading: Boolean,
            hasDiff: Boolean,
            editable: {
                type: Boolean,
                default: true
            },
            viewValue: { // 查看值模式，不需要要编辑表单操作
                type: Boolean,
                default: false
            },
            cols: {
                type: Array
            },
            config: { // 资源筛选表单值
                type: Object,
                default () {
                    return {}
                }
            },
            value: { // 表格值
                type: Array,
                default () {
                    return []
                }
            },
            separator: String
        },
        data () {
            return {
                cellOption: {
                    showGroup: false,
                    showHook: false,
                    showLabel: false,
                    formMode: false
                },
                editRow: '',
                tableData: tools.deepClone(this.value),
                pagination: {
                    current: 1,
                    count: this.value.length,
                    limit: 10,
                    'show-limit': false
                },
                i18n: {
                    resourceFilter: gettext('资源筛选'),
                    export: gettext('导出'),
                    import: gettext('导入'),
                    edit: gettext('编辑'),
                    delete: gettext('删除'),
                    save: gettext('保存'),
                    cancel: gettext('取消')
                }
            }
        },
        computed: {
            dataList () {
                const { current, limit } = this.pagination
                const start = (current - 1) * limit
                return this.tableData.slice(start, start + limit)
            }
        },
        watch: {
            value: {
                handler (val) {
                    this.tableData = tools.deepClone(val)
                    this.pagination.count = val.length
                }
            },
            deep: true
        },
        methods: {
            renderTableHeader (h, { column, $index }) {
                return h('p', {
                    class: 'label-text',
                    directives: [{
                        name: 'bk-overflow-tips'
                    }]
                }, [
                    column.label
                ])
            },
            exportData () {
                const sheetHeader = []
                this.cols.forEach(item => {
                    const tagCode = item.config.tag_code
                    const name = item.config.attrs.name
                    if (tagCode !== 'tb_btns') {
                        const headerName = item.config.module ? name : `${name}(${tagCode})`
                        sheetHeader.push(headerName)
                    }
                })
                const sheetValue = this.value.map(rowData => {
                    const dataItem = []
                    this.cols.forEach(col => {
                        const tagCode = col.config.tag_code
                        if (tagCode !== 'tb_btns') {
                            dataItem.push(rowData[col.config.tag_code][col.config.tag_code])
                        }
                    })
                    return dataItem
                })
                const sheetData = [sheetHeader, ...sheetValue]

                const wsName = 'Sheet1'
                const wb = XLSX.utils.book_new()
                const ws = XLSX.utils.aoa_to_sheet(sheetData)
                XLSX.utils.book_append_sheet(wb, ws, wsName)
                XLSX.writeFile(wb, 'resource_data.xlsx')
            },
            importData (file) {
                const types = file.name.split('.')[1]
                const fileTypeValid = ['xlsx', 'xlc', 'xlm', 'xls', 'xlt', 'xlw', 'csv'].some(item => item === types)
                if (!fileTypeValid) {
                    this.$bkMessage({
                        theme: 'error',
                        message: gettext('格式错误！请选择xlsx,xls,xlc,xlm,xlt,xlw或csv文件'),
                        delay: 10000
                    })
                    return
                }
                this.readFileData(file).then(data => {
                    if (data && data.length > 0) {
                        this.$emit('importData', data[0].sheet)
                        this.pagination.current = 1
                    }
                })
            },
            // 将本地Excel文件的二进制数据转化为json数据
            readFileData (file) {
                return new Promise(function (resolve, reject) {
                    const reader = new FileReader()
                    reader.onload = function (e) {
                        const data = e.target.result
                        const wb = XLSX.read(data, {
                            type: 'binary'
                        })
                        const result = []
                        wb.SheetNames.forEach((sheetName) => {
                            result.push({
                                sheetName: sheetName,
                                sheet: XLSX.utils.sheet_to_json(wb.Sheets[sheetName])
                            })
                        })
                        resolve(result)
                    }
                    reader.readAsBinaryString(file.raw)
                })
            },
            updateDiffData () {
                this.$refs.diffAlert.handleClose()
                this.$emit('handleDiff')
            },
            validate () {
                this.$refs.tableForm.validate()
            }
        }
    }
</script>
<style lang="scss" scoped>
    .opt-btns {
        margin-bottom: 10px;
        /deep/ .bk-button {
            font-size: 12px;
        }
        /deep/ .upload-btn {
            display: inline-block;
            font-size: 12px;
        }
    }
    .diff-alert {
        display: flex;
        justify-content: space-between;
        align-items: center;
        /deep/ .bk-link-text {
            font-size: 12px;
        }
    }
    .alert-disabled {
        color: #ccc;
        cursor: not-allowed;
        /deep/ .bk-link-text {
            color: #ccc;
            cursor: not-allowed;
        }
    }
</style>
