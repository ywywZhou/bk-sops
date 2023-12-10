<template>
    <section class="info-section log-section" data-test-id="taskExecute_form_nodeLog">
        <div class="log-wrap">
            <!-- 内置插件/第三方插件tab -->
            <bk-tab
                v-if="isThirdPartyNode && !isLogLoading"
                :active-bar="{
                    position: 'top',
                    height: '2px'
                }"
                :class="{ 'empty-tab': !logInfo && !thirdPartyNodeLog }"
                :active.sync="curPluginTab"
                type="unborder-card">
                <bk-tab-panel v-bind="{ name: 'build_in_plugin', label: $t('平台日志') }"></bk-tab-panel>
                <bk-tab-panel
                    v-bind="{ name: 'third_party_plugin', label: $t('第三方插件日志') }">
                </bk-tab-panel>
            </bk-tab>
            <div class="perform-log" v-bkloading="{ isLoading: isLogLoading, opacity: 1, zIndex: 100 }">
                <full-code-editor
                    v-if="logInfo || thirdPartyNodeLog"
                    ref="fullCodeEditor"
                    class="scroll-editor"
                    :key="curPluginTab"
                    :options="{
                        scrollBeyondLastLine: false
                    }"
                    :value="curPluginTab === 'build_in_plugin' ? logInfo : thirdPartyNodeLog">
                    <div slot="tool" class="refresh-wrapper">
                        <bk-dropdown-menu trigger="click" align="left" ref="dropdown">
                            <span
                                slot="dropdown-trigger"
                                class="auto-refresh">
                                <i class="bk-icon icon-refresh"></i>
                                <span class="intervals">{{ intervalInfo.time ? intervalInfo.name : 'off'}}</span>
                            </span>
                            <div class="more-interval-html" slot="dropdown-content">
                                <ul class="interval-list">
                                    <li
                                        :class="['interval-item', { 'active': intervalInfo.time === item.time }]"
                                        v-for="item in intervalList"
                                        :key="item.time"
                                        @click="intervalInfo = item">
                                        {{ item.name }}
                                    </li>
                                </ul>
                            </div>
                        </bk-dropdown-menu>
                        <i class="bk-icon icon-refresh" @click="onRefresh"></i>
                    </div>
                </full-code-editor>
                <NoData v-else :message="$t('暂无日志')"></NoData>
            </div>
        </div>
    </section>
</template>

<script>
    import { mapActions } from 'vuex'
    import FullCodeEditor from '@/components/common/FullCodeEditor.vue'
    import NoData from '@/components/common/base/NoData.vue'
    
    const intervalList = [
        { name: '关闭 (off)', time: 0 },
        { name: '1s', time: 1000 },
        { name: '5s', time: 5 * 1000 },
        { name: '10s', time: 10 * 1000 },
        { name: '30s', time: 30 * 1000 },
        { name: '1m', time: 60 * 1000 },
        { name: '3m', time: 3 * 60 * 1000 },
        { name: '5m', time: 5 * 60 * 1000 }
    ]
    export default {
        name: 'NodeLog',
        components: {
            FullCodeEditor,
            NoData
        },
        props: {
            nodeDetailConfig: {
                type: Object,
                default: () => ({})
            },
            executeInfo: {
                type: Object,
                default: () => ({})
            },
            thirdPartyNodeCode: {
                type: String,
                default: ''
            },
            adminView: {
                type: Boolean,
                default: false
            },
            engineVer: {
                type: Number,
                required: true
            }
        },
        data () {
            return {
                curPluginTab: 'build_in_plugin',
                isLogLoading: false,
                logInfo: '',
                thirdPartyNodeLog: '',
                scrollId: '',
                observer: null,
                editScrollDom: null,
                nodeLogPageInfo: null,
                logExecInfo: {
                    loading: false,
                    timer: null
                },
                thirdLogExecInfo: {
                    loading: false,
                    timer: null
                },
                intervalInfo: {
                    time: 0,
                    name: '关闭 (off)'
                },
                intervalList,
                needScrollBottom: false,
                lastPageLog: null
            }
        },
        computed: {
            isThirdPartyNode () {
                const compCode = this.nodeDetailConfig.component_code
                return compCode && compCode === 'remote_plugin'
            }
        },
        watch: {
            'intervalInfo.time' (val, oldVal) {
                if (!oldVal) {
                    this.needScrollBottom = true
                }
                if (val) {
                    this.editScrollDom = null
                    this.destroyObserver()
                    this.pollingNodeLog()
                } else {
                    clearTimeout(this.logExecInfo.timer)
                    clearTimeout(this.thirdLogExecInfo.thirdTimer)
                    this.watchEditorScroll()
                }
            },
            curPluginTab () {
                this.scrollBottom()
                if (!this.intervalInfo.time) {
                    this.watchEditorScroll()
                }
            }
        },
        beforeDestroy () {
            this.intervalInfo = {
                time: 0,
                name: '关闭 (off)'
            }
            this.destroyObserver()
            clearTimeout(this.logExecInfo.timer)
            clearTimeout(this.thirdLogExecInfo.thirdTimer)
        },
        mounted () {
            this.initLog()
        },
        methods: {
            ...mapActions('task/', [
                'getEngineVerNodeLog',
                'getNodeExecutionRecordLog'
            ]),
            ...mapActions('atomForm/', [
                'loadPluginServiceLog'
            ]),
            ...mapActions('admin/', [
                'taskflowHistroyLog'
            ]),
            initLog () {
                const { state, history_id, version, outputs } = this.executeInfo
                // 获取节点日志
                if (state && !['READY', 'CREATED'].includes(state)) {
                    const query = Object.assign({}, this.nodeDetailConfig, {
                        history_id: history_id,
                        version: version
                    })
                    this.isLogLoading = true
                    const asyncFunc = [this.getPerformLog(query)]
                    // 获取第三方插件节点日志
                    if (this.isThirdPartyNode) {
                        const traceId = outputs.length && outputs[0].value
                        asyncFunc.push(this.handleTabChange(traceId))
                    }
                    Promise.all(asyncFunc).then(() => {
                        this.isLogLoading = false
                        // 滚动加载
                        this.scrollBottom()
                        this.watchEditorScroll()
                    }).catch(() => {
                        this.isLogLoading = false
                    })
                }
            },
            // 非admin 用户执行记录
            async getPerformLog (query) {
                try {
                    this.logExecInfo.loading = true
                    let performLog = {}
                    if (this.adminView) { // 管理端日志
                        performLog = await this.taskflowHistroyLog(query)
                    } else if (this.engineVer === 1) { // 不同引擎版本的任务调用不同的接口
                        performLog = await this.getNodeExecutionRecordLog(query)
                    } else if (this.engineVer === 2) {
                        performLog = await this.getEngineVerNodeLog(query)
                    }
                    const respLog = this.adminView ? performLog.data.log : performLog.data
                    // 如果已经获取过最后一页数据，再次获取时把上一次记录的覆盖掉
                    if (this.lastPageLog) {
                        this.lastPageLog = respLog
                        this.logInfo = this.logInfo.replace(this.lastPageLog, respLog)
                    } else {
                        // 判断是否为最后一页
                        const { total: respTotal, page_size } = performLog.page
                        const respLastPage = Math.ceil(respTotal / page_size)
                        this.lastPageLog = query.page === respLastPage ? respLog : null

                        this.logInfo = this.logInfo + (this.logInfo ? '\n' : '') + respLog
                    }
                    this.nodeLogPageInfo = performLog.page
                    this.logExecInfo.loading = false
                    // 滚动到底部
                    if (this.needScrollBottom || this.isEditorScrolledToBottom()) {
                        this.needScrollBottom = false
                        this.$nextTick(() => {
                            this.scrollBottom()
                        })
                    }
                    // 自动加载
                    if (this.intervalInfo.time) {
                        this.pollingNodeLog()
                    }
                } catch (e) {
                    console.log(e)
                    this.isLogLoading = false
                }
            },
            pollingNodeLog () {
                if (!this.logExecInfo.loading) {
                    this.logExecInfo.loading = true
                    this.logExecInfo.timer = setTimeout(() => {
                        const { history_id, version } = this.executeInfo
                        const { page, total, page_size } = this.nodeLogPageInfo
                        const nextPage = page === Math.ceil(total / page_size) ? page : page + 1
                        const query = Object.assign({}, this.nodeDetailConfig, {
                            page: nextPage,
                            history_id,
                            version
                        })
                        this.getPerformLog(query)
                    }, this.intervalInfo.time)
                }
                if (this.isThirdPartyNode && !this.thirdLogExecInfo.loading && this.scrollId) {
                    this.thirdLogExecInfo.loading = true
                    this.thirdLogExecInfo.timer = setTimeout(() => {
                        const { outputs } = this.executeInfo
                        const traceId = outputs.length && outputs[0].value
                        this.handleTabChange(traceId)
                    }, this.intervalInfo.time)
                }
            },
            scrollBottom () {
                let editor = this.$refs.fullCodeEditor
                editor = editor && editor.$refs.codeEditor
                const { monacoInstance } = editor || {}
                if (monacoInstance) {
                    const contentHeight = monacoInstance.getContentHeight()
                    monacoInstance.setScrollTop(contentHeight)
                }
            },
            isEditorScrolledToBottom () {
                let editor = this.$refs.fullCodeEditor
                editor = editor && editor.$refs.codeEditor
                const { monacoInstance } = editor || {}
                if (monacoInstance) {
                    const scrollHeight = monacoInstance.getScrollHeight()
                    const scrollTop = monacoInstance.getScrollTop()
                    const clientHeight = monacoInstance.getLayoutInfo().height
                    return scrollHeight - scrollTop === clientHeight
                }
                return false
            },
            destroyObserver () {
                if (this.observer) {
                    this.observer.disconnect()
                    this.observer.takeRecords()
                    this.observer = null
                }
            },
            // 手动刷新
            onRefresh () {
                this.needScrollBottom = true
                this.pollingNodeLog()
            },
            watchEditorScroll () {
                // 第三方日志滚动加载
                this.$nextTick(() => {
                    // 滚动dom
                    const editScrollDom = document.querySelector('.scroll-editor .code-editor .vertical .slider')
                    if (!editScrollDom) return
                    // 编辑器dom
                    const editDom = document.querySelector('.scroll-editor .monaco-editor')
                    const MutationObserver = window.MutationObserver || window.WebKitMutationObserver || window.MozMutationObserver

                    // 监听滚动dom
                    this.observer = new MutationObserver(mutation => {
                        const { height } = editScrollDom.getBoundingClientRect()
                        const { height: editHeight } = editDom && editDom.getBoundingClientRect()
                        const top = editScrollDom.offsetTop
                        const offsetBottom = editHeight > 300 ? 180 : 80
                        if (this.curPluginTab === 'third_party_plugin') {
                            if (editHeight - height - top < offsetBottom && !this.thirdLogExecInfo.loading && this.scrollId) {
                                const { outputs } = this.executeInfo
                                const traceId = outputs.length && outputs[0].value
                                this.handleTabChange(traceId)
                            }
                        } else if (this.nodeLogPageInfo) {
                            if (editHeight - height - top < offsetBottom && !this.logExecInfo.loading) {
                                const { page, total, page_size } = this.nodeLogPageInfo
                                const nextPage = page === Math.ceil(total / page_size) ? page : page + 1
                                const { history_id, version } = this.executeInfo
                                const query = Object.assign({}, this.nodeDetailConfig, {
                                    page: nextPage,
                                    history_id,
                                    version
                                })
                                this.getPerformLog(query)
                            }
                        }
                    })
                    this.observer.observe(editScrollDom, {
                        childList: true,
                        attributes: true,
                        characterData: true,
                        subtree: true
                    })
                    this.editScrollDom = editScrollDom
                })
            },
            async handleTabChange (traceId) {
                try {
                    this.thirdLogExecInfo.loading = true
                    const resp = await this.loadPluginServiceLog({
                        plugin_code: this.thirdPartyNodeCode,
                        trace_id: traceId,
                        scroll_id: this.scrollId || undefined
                    })
                    if (!resp.result) {
                        this.scrollId = ''
                        return
                    }
                    const { logs, scroll_id } = resp.data
                    const thirdPartyLogs = this.thirdPartyNodeLog || ''
                    this.thirdPartyNodeLog = thirdPartyLogs + logs
                    this.scrollId = scroll_id
                    this.thirdLogExecInfo.loading = false
                    // 滚动到底部
                    if (this.needScrollBottom || this.isEditorScrolledToBottom()) {
                        this.needScrollBottom = false
                        this.$nextTick(() => {
                            this.scrollBottom()
                        })
                    }
                    // 自动加载
                    if (this.intervalInfo.time) {
                        this.pollingNodeLog()
                    }
                } catch (error) {
                    console.warn(error)
                    this.isLogLoading = false
                }
            }
        }
    }
</script>

<style lang="scss" scoped>
    @import '@/scss/mixins/scrollbar.scss';
    .log-section {
        height: 100%;
        .log-wrap {
            height: calc(100% - 10px);
            display: flex;
            flex-direction: column;
            position: relative;
            /deep/.bk-tab {
                position: absolute;
                z-index: 2;
                height: 40px;
                .bk-tab-header,
                .bk-tab-label-list {
                    height: 40px !important;
                }
                .bk-tab-label-item {
                    line-height: 40px !important;
                    &.active {
                        color: #fff;
                    }
                }
                .bk-tab-section {
                    padding: 0;
                }
                &.empty-tab {
                    width: 100%;
                    background: #2e2e2e;
                }
            }
            .full-code-editor {
                margin: 0 !important;
                /deep/.tool-area {
                    height: 40px;
                    display: flex;
                    align-items: center;
                    justify-content: flex-end;
                    background: #2e2e2e;
                    .bk-icon {
                        color: #c4c6cc;
                        cursor: pointer;
                        &.icon-copy-shape {
                            margin-right: 14px !important;
                        }
                    }
                    .refresh-wrapper {
                        position: relative;
                        display: flex;
                        margin-right: 25px;
                        .auto-refresh {
                            display: flex;
                            margin-right: 12px;
                            cursor: pointer;
                            i {
                                font-size: 16px;
                            }
                        }
                        .interval-list {
                            height: 200px;
                            width: 100px;
                            padding: 4px 0;
                            background: #fff;
                            overflow-y: auto;
                            @include scrollbar;
                            .interval-item {
                                height: 32px;
                                line-height: 32px;
                                padding: 0 12px;
                                font-size: 12px;
                                color: #63656e;
                                text-decoration: none;
                                white-space: nowrap;
                                cursor: pointer;
                                &:hover {
                                    background-color: #f5f7fa;
                                }
                                &.active {
                                    color: #3a84ff;
                                    background: #e1ecff;
                                }
                            }
                        }
                        .intervals {
                            line-height: 16px;
                            margin-left: 4px;
                            font-size: 12px;
                            color: #c4c6cc;
                        }
                        &::after {
                            content: '';
                            display: inline-block;
                            position: absolute;
                            top: 0;
                            right: -13px;
                            width: 1px;
                            height: 16px;
                            background: #979ba5;
                        }
                    }
                }
                /deep/.code-editor {
                    height: calc(100% - 40px);
                }
            }
        }
        .perform-log {
            height: 100%;
        }
        .no-data-wrapper {
            height: initial;
            margin-top: 100px;
        }
    }
</style>
