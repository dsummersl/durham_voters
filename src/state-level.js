const _ = require('lodash')
const d3 = require('d3')
const extend = require('xtend')
const html = require('choo/html')
const topojson = require('topojson-client')

// TODO how to filter to one county:
const COUNTY = 'DURHAM'
const COUNTY_ID = 32

const computePrecinctVotes = (state, precinct, county) => {
  let match = _.filter(state.filteredCsvData, {
    'Precinct': precinct,
    'County': county
  })
  if (match.length === 0) {
    match = _.filter(state.filteredCsvData, {
      'Precinct': '0'+ precinct,
      'County': county
    })
  }
  if (match.length === 0) {
    return -1
  }
  return match[0].Total_Votes
}

const computeAllVotes = (state, precinct, county) => {
  return _.chain(state.voteSummary)
    .filter({
      'Precinct': precinct,
      'County': county
    })
    .map('Count')
    .sum()
    .value()
}

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

  return (state, send) => {
    if (!state.precincts || state.filteredCsvData.length === 0) {
      return el
    }

    state.precincts.features = _.filter(state.precincts.features, _.matchesProperty('properties', { 'COUNTY_NAM': COUNTY }))

    let computePercent = ((d) => {
      const TOTAL_VOTES = computePrecinctVotes(state, d.properties.PREC_ID, d.properties.COUNTY_NAM)
      if (TOTAL_VOTES === -1) {
        return color(0)
      }
      const PRECINCT = d.properties.PREC_ID.replace(/^0+/, '')
      return TOTAL_VOTES / computeAllVotes(state, PRECINCT, d.properties.COUNTY_NAM)
    })

    // Compute the bounds of a feature of interest, then derive scale & translate.
    const b = path.bounds(state.precincts)

    // height / width
    const leftTop = b[0]
    const rightBottom = b[1]
    const ratio = (rightBottom[1] - leftTop[1]) / (rightBottom[0] - leftTop[0])
    // Assume that width of the screen > height of screen:
    let width = el.offsetWidth
    let height = width * ratio
    // When the ratio > 1 the object is taller than it is wide: resize to
    // available height:
    if (ratio > 1.0) {
      height = el.offsetHeight
      width = height * ratio
    }
    d3.select('svg').style('height', height)

    const s = 0.9 / Math.max(
      (rightBottom[0] - leftTop[0]) / width,
      (rightBottom[1] - leftTop[1]) / height
    )
    const t = [
      (width - s * (rightBottom[0] + leftTop[0])) / 2,
      (height - s * (rightBottom[1] + leftTop[1])) / 2
    ]

    projection.scale(s)
        .translate(t)

    const color = d3.scaleLinear()
      .domain([0, 1])
      .range(["white", "black"])

    const boundPaths = svg.selectAll('path').data(state.precincts.features)
    let enter = boundPaths.enter()

    enter.append('path')
        .attr('class', 'county')
        .attr('d', path)
        .style('fill', 'white')
        .on('click', function(d) {
          send('stateLevel:selectPrecinct', { precinct: d.properties.PREC_ID })
        })
      .merge(boundPaths)
        .transition()
        .style('fill', (d) => {
          if (d.properties.PREC_ID === state.selectedPrecinct) {
            return color(computePercent(d) + 0.2)
          }
          return color(computePercent(d))
        })

    const boundText = svg.selectAll('text').data(state.precincts.features)
    enter = boundText.enter()
    enter.append('text')
        .style('text-anchor', 'middle')
        .style('fill', 'white')
        .on('click', function(d) {
          send('stateLevel:selectPrecinct', { precinct: d.properties.PREC_ID })
        })
        .attr('transform', (d) => {
          return `translate(${path.centroid(d)}) scale(0.5)`
        })
      .merge(boundText)
        .transition()
        .style('fill', (d) => color(computePercent(d) + 0.1))
        .text((d) => {
          return `${parseInt(computePercent(d)*100)}%`
        })

    return el
  }
})()

module.exports.model = (app) => {
  app.model({
    namespace: 'stateLevel',
    state: {
      names: [ '...loading...' ],
      choiceIndex: 0,
      csvData: [ ],
      filteredCsvData: [],
      selectedPrecinct: '',
      selectedCounty: COUNTY,
      selectedCountyId: COUNTY_ID,
      precincts: null
    },
    effects: {
      loadData: (state, data, send, done) => {
        var loaded = _.after(4, done)

        d3.csv('./county_32_vote_summary.csv', (d) => {
          return {
            CountyId: d.county_id,
            County: 'DURHAM',
            Precinct: d.precinct_desc,
            Party: d.party_cd,
            Voted: d.Voted === 'TRUE',
            Count: +d.N
          }
        }, (rows) => {
          send('stateLevel:processVoteSummary', rows, loaded)
        })
        d3.csv('./president.csv', (d) => {
          return {
            Precinct: d.Precinct,
            County: d.County,
            Choice: d.Choice,
            Total_Votes: +d.Total_Votes
          }
        }, (rows) => {
          send('stateLevel:processElectionData', rows, loaded)
        })
        d3.json("./Precincts.topojson", (error, nc) => {
          if (error) return console.log(error)

          const boundaries = topojson.feature(nc, nc.objects.Precincts)
          send('stateLevel:receiveTopoJson', boundaries, loaded)
        })
      },
      processElectionData: (state, csv, send, done) => {
        const names = _.chain(csv).map('Choice').uniq().value()
        const filtered = _.filter(csv, { 'Choice': names[state.choiceIndex] })
        send('stateLevel:receiveElectionData', {
          names: names,
          csvData: csv,
          filteredCsvData: filtered,
        }, done)
      },
      processVoteSummary: (state, csv, send, done) => {
        send('stateLevel:receiveVoteSummary', {
          voteSummary: csv
        }, done)
      },
      selectName: (state, data, send, done) => {
        send('stateLevel:receiveChoiceIndex', data, (err, res) => {
          if (err) return console.log(err)
          send('stateLevel:processElectionData', res.stateLevel.csvData, done)
        })
      }
    },
    reducers: {
      receiveElectionData: (state, data) => {
        return extend(state, {
          names: data.names,
          csvData: data.csvData,
          filteredCsvData: data.filteredCsvData
        })
      },
      receiveVoteSummary: (state, data) => {
        return extend(state, {
          voteSummary: data.voteSummary
        })
      },
      receiveTopoJson: (state, data) => {
        return extend(state, {
          precincts: data
        })
      },
      receiveChoiceIndex: (state, data) => {
        return extend(state, {
          choiceIndex: +data.choiceIndex
        })
      },
      selectPrecinct: (state, data) => {
        return extend(state, {
          selectedPrecinct: data.precinct
        })
      }
    }
  })
}

module.exports.view = (state, prev, send) => {
  console.log("|state.stateLevel.selectedPrecinct = "+ state.stateLevel.selectedPrecinct);
  console.log(computeAllVotes(state.stateLevel, state.stateLevel.selectedPrecinct, state.stateLevel.selectedCounty))
  return html`
    <div onload=${() => send('stateLevel:loadData')}>
      <div class="container-fluid">
        <nav class="navbar navbar-fixed-top navbar-dark bg-primary">
          <ul class="nav navbar-nav">
            <form class="form-inline float-xs-left">
              <label for="selectData">Candidate: </label>
              <select class="form-control" id="selectData" onchange=${(e) => {
                send('stateLevel:selectName', { choiceIndex: e.target.value })
              }}>
                ${state.stateLevel.names.map((name, index) => html`
                    <option value="${index}" ${index == state.stateLevel.choiceIndex ? 'selected':''}>${name}</option>
                  `)}
              </select>
            </form>
          </ul>
        </nav>

        <div class="row">
          <div class="col-md-6 map-container">
            ${mapElement(state.stateLevel, send)}
          </div>
          <div class="col-md-6">
            <h1>Summary</h1>
            <p>
              Percent of voters that voted for ${state.stateLevel.names[state.stateLevel.choiceIndex]}.
            </p>
            <table class="table">
              <thead>
                <th>Description</th>
                <th>Value</th>
              </thead>
              <tbody>
                <tr>
                  <td>Precinct</td>
                  <td>${state.stateLevel.selectedPrecinct}</td>
                </tr>
                <tr>
                  <td>All Votes</td>
                  <td>${computeAllVotes(state.stateLevel, state.stateLevel.selectedPrecinct, state.stateLevel.selectedCounty)}</td>
                </tr>
                <tr>
                  <td>Votes for ${state.stateLevel.names[state.stateLevel.choiceIndex]}</td>
                  <td>${computePrecinctVotes(state.stateLevel, state.stateLevel.selectedPrecinct, state.stateLevel.selectedCounty)}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>`
}
