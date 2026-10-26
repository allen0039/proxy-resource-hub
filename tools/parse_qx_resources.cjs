#!/usr/bin/env node
// Execute the configured resource parser in a bounded context with no I/O APIs.
const fs = require('fs');
const vm = require('vm');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const results = input.resources.map(resource => {
  const completed = [], notifications = [];
  let content = resource.content, error = null;
  if (resource.parser) {
    try {
      vm.runInNewContext(input.parser, {
        $resource: {link: resource.url, content, type: resource.type || 'filter', tag: resource.tag},
        $environment: {version: 'Quantumult X build 1000'},
        $done: value => completed.push(value),
        $notify: (...args) => notifications.push(args.map(String)),
        $prefs: {valueForKey: () => null, setValueForKey: () => true},
        console: {log: () => {}},
      }, {timeout: 15000});
      content = completed.at(-1)?.content || '';
    } catch (e) { error = String(e); }
  }
  return {url: resource.url, content, error, notifications};
});
process.stdout.write(JSON.stringify(results));
