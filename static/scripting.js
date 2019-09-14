/* Copyright 2019 Matthew Bishop
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

(function() {

/*
 * Downloads entries from REST API, then renders them to the given element.
 *
 * @param {string} feedsUrl The REST URL to download the feeds from.
 * @param {string} templateId The ID of the Handlebars template to use for the render.
 * @param {string} destinationId The ID of the destination element to render the feed template to.
 */
function refreshEntries(feedsUrl, templateId, destinationId) {
    $.get(feedsUrl, function(data, status) {
        let source = $(templateId).html();
        let template = Handlebars.compile(source);
        let html = template(data);
        $(destinationId).html(html);
    });
}

/**
 * Click event handler for feedRefresh button.
 *
 * @param {Event} event The jQuery event. Currently unused.
 */
function feedRefresh_click(event) {
    console.log(typeof event.constructor);
    refreshEntries('/entries', '#entries-template', '#entries-table');
}

// perform logic that needs the DOM to have finished loading
$(document).ready(function(){
    // attach logic to events
    $('#feedRefresh').click(feedRefresh_click);

    // initial load of feed entries
    refreshEntries('/entries', '#entries-template', '#entries-table');
});

})();
