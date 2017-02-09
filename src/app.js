require('./app.css')

const choo = require('choo')
const stateLevel = require('./state-level')

const app = choo()
stateLevel.model(app)

app.router(
  [ '/', stateLevel.view ]
)

const tree = app.start()
document.body.appendChild(tree)
