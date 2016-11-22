require('./app.css')

const extend = require('xtend')
const d3 = require('d3')
const topojson = require('topojson-client')
const choo = require('choo')
const html = require('choo/html')
const app = choo()

app.model({
  state: {
    todos: [ ]
  },
  reducers: { }
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

var svg = d3.select("#map").append("svg")
    .attr("width", '100%')

var projection = d3.geoAlbers()
    .scale(1)
    .translate([0, 0])
    .rotate([79.6,-34.5,-1])

var path = d3.geoPath()
    .projection(projection)

d3.json("./Precincts.topojson", function(error, nc) {
  if (error) throw error

  const boundaries = topojson.feature(nc, nc.objects.Precincts)

  // Compute the bounds of a feature of interest, then derive scale & translate.
  const b = path.bounds(boundaries)

  // height / width
  const ratio = (b[1][1] - b[0][1]) / (b[1][0] - b[0][0])
  const width = document.getElementById('map').offsetWidth
  const height = width * ratio

  const s = 0.95 / Math.max((b[1][0] - b[0][0]) / width, (b[1][1] - b[0][1]) / height)
  const t = [(width - s * (b[1][0] + b[0][0])) / 2, (height - s * (b[1][1] + b[0][1])) / 2]

  projection.scale(s)
      .translate(t)

  svg.selectAll('path').data(boundaries.features)
    .enter().append('path')
      .attr('class', 'county')
      .attr('d', path)

  let onSizeChange = () => {
    // TODO not quite working.
    const newWidth = document.getElementById('map').offsetWidth
    d3.select('svg > g').attr('transform', `scale(${ newWidth / width })`)
    d3.select('svg').style('height', height * (newWidth / width))
  }

  d3.select(window).on('resize', onSizeChange)

  onSizeChange()
})
