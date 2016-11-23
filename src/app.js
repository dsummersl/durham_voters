require('./app.css')

const choo = require('choo')
const d3 = require('d3')
const extend = require('xtend')
const html = require('choo/html')
const _ = require('lodash')
const topojson = require('topojson-client')

const app = choo()
app.model({
  state: {
    names: [ '...loading...' ],
    csvData: [  ],
    precincts: null
  },
  effects: {
    loadData: (data, state, send, done) => {
      var loaded = _.after(3, done)

      d3.csv('./president.csv', (rows) => {
        const names = _.chain(rows).map('Choice').uniq().value()
        send('recieveNames', names, loaded)
        send('receiveElectionData', rows, loaded)
      })
      d3.json("./Precincts.topojson", (error, nc) => {
        if (error) return console.log(error)

        const boundaries = topojson.feature(nc, nc.objects.Precincts)
        send('receiveTopoJson', boundaries, loaded)
      })
    }
  },
  reducers: {
    receiveElectionData: (electionData, state) => {
      return extend(state, {
        csvData: extend(electionData)
      })
    },
    recieveNames: (data, state) => {
      return extend(state, {
        names: data
      })
    },
    receiveTopoJson: (data, state) => {
      return extend(state, {
        precincts: data
      })
    }
  }
})

const mapElement = (() => {
  const el = document.createElement('div')
  el.classList.add('map')

  let svg = d3.select(el).append("svg")
      .attr("width", '100%')

  let projection = d3.geoAlbers()
      .scale(1)
      .translate([0, 0])
      .rotate([79.6,-34.5,-1])

  let path = d3.geoPath()
      .projection(projection)

  // let onSizeChange = () => {
  //   // TODO not quite working.
  //   const newWidth = el.offsetWidth
  //   d3.select('svg > g').attr('transform', `scale(${ newWidth / width })`)
  //   d3.select('svg').style('height', height * (newWidth / width))
  // }
  //
  // d3.select(window).on('resize', onSizeChange)

  return (state) => {
    if (!state.precincts) {
      return el
    }

    // Compute the bounds of a feature of interest, then derive scale & translate.
    const b = path.bounds(state.precincts)

    // height / width
    const ratio = (b[1][1] - b[0][1]) / (b[1][0] - b[0][0])
    const width = el.offsetWidth
    const height = width * ratio
    d3.select('svg').style('height', height)

    const s = 0.95 / Math.max((b[1][0] - b[0][0]) / width, (b[1][1] - b[0][1]) / height)
    const t = [(width - s * (b[1][0] + b[0][0])) / 2, (height - s * (b[1][1] + b[0][1])) / 2]

    projection.scale(s)
        .translate(t)

    svg.selectAll('path').data(state.precincts.features)
      .enter().append('path')
        .attr('class', 'county')
        .attr('d', path)

    return el
  }
})()

const view = (state, prev, send) => {
  return html`
    <div onload=${() => send('loadData')}>
      <div class="container-fluid">
        <nav class="navbar navbar-fixed-top navbar-dark bg-primary">
          <ul class="nav navbar-nav">
            <form class="form-inline float-xs-left">
              <label for="selectData">Date</label>
              <select class="form-control" id="selectData">
                ${state.names.map((name) => html`
                    <option value="${name}">${name}</option>
                  `)}
              </select>
            </form>
          </ul>
        </nav>
      </div>

      ${mapElement(state)}
    </div>`
}

app.router((route) => [
  route('/', view)
])

const tree = app.start()
document.body.appendChild(tree)
