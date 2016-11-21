require('./app.css')

const extend = require('xtend')
const choo = require('choo')
const html = require('choo/html')
const app = choo()

app.model({
  state: {
    todos: [ ]
  },
  reducers: {
    addTodo: (data, state) => {
      const todo = extend(data, {
        completed: false
      })
      const newTodos = state.todos.slice()
      newTodos.push(todo)
      return { todos: newTodos }
    }
  }
})

const view = (state, prev, send) => {
  return html`
    <div>
      <form onsubmit=${(e) => {
        const input = e.target.children[0]
        send('addTodo', { title: input.value })
        input.value = ''
        e.preventDefault()
      }}>
        <input type="text" placeholder="New item" id="title">
      </form>
      <ul>
        ${state.todos.map((todo) => html`
          <li>
            <input type="checkbox" ${todo.completed ? 'checked':''} />
            ${todo.title}
          </li>`)}
      </ul>
    </div>`
}

app.router((route) => [
  route('/', view)
])

const tree = app.start()
document.getElementById('map').appendChild(tree)
