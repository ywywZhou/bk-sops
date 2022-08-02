
// 获取数组最后一个元素
const last = (arr) => arr[arr.length - 1]

class History {
    constructor () {
        //
        this.initValue = null
        // 撤销
        this.undoStack = []
        // 重做
        this.redoStack = []
        // 最新的值
        this.currentValue = null
        // 最大历史长度
        this.maxLength = 20
    }

    /**
     * 模板初始历史记录
     * @param {*} value 历史记录值
     */
    init (value) {
        this.initValue = value
    }

    /**
     * 添加历史记录
     * @param {*} value 历史记录值
     */
    push (value) {
        if (this.currentValue !== value) {
            this.undoStack.push(value)
        }
        this.redoStack = []
        if (this.undoStack.length > this.maxLength) {
            this.undoStack.splice(0, 1)
        }
    }

    /**
     * 撤销
     */
    undo () {
        if (this.undoStack.length === 0) {
            return false
        }
        const value = this.undoStack.pop()
        this.redoStack.push(value)
        this.currentValue = this.undoStack.length ? last(this.undoStack) : this.initValue
    }

    /**
     * 重做
     */
    redo () {
        if (this.redoStack.length === 0) {
            return false
        }
        const value = this.redoStack.pop()
        this.undoStack.push(value)
        this.currentValue = value
    }

    /**
     * 清空
     */
    clear () {
        this.undoStack = []
        this.redoStack = []
        this.currentValue = null
        this.initValue = null
    }
}

export default new History({})
