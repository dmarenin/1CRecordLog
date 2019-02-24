window.r_ref = '';

var items;
var items_unselected;
var items_garant;

var items_test;

var _items;
var items_test;

var groups;
var timeline;
var container;

var is_garant;

var properties_select;

var links;

is_garant = false;

let selected_mp = []; // выбранный мастер-приёмщик (on select)
let selected_equipment = []; // выбранное оборудование (on select)

let all_selected_items = []; // реализуем список выбранных итемов для обычного клика ЛКМ (без Ctrl+Click или long pressing)
let all_selected_items_ids = {}; // список соответствия ID => gen.id(start-end-d_ref)

container = document.getElementById('visualization');
timeline = new vis.Timeline(container, [], {});

timeline.on('select', function (properties) 
{
    if (window.editable != '1')
    {
        thisItem = timeline.itemsData._data[properties.items];
        if (!thisItem || (thisItem && (!thisItem['className'] || (thisItem['className'] && thisItem['className'] != 'expected' && thisItem['className'] != 'not_is_guarantee')))) //exit on expected
        {
            setTimeout(setSelection, 500, properties);
        }
        else if (window.readonly != '1')
        {
            // rebuild selection
            let MPcount = 0;
            let Equipcount = 0;
            selected_mp = [];
            selected_equipment = [];
            
            // check new item
            let thisNewItem = timeline.itemsData._data[properties.items[0]];
            if (thisNewItem && thisNewItem['className'] && thisNewItem['className'] == 'expected')
            {
              //"double" check
              if (getItemByText(all_selected_items, properties.items[0]))
              {
                //clear
                delete all_selected_items[getKeyByText(all_selected_items, properties.items[0])];
                //if (all_selected_items_ids[properties.items[0]]) { delete all_selected_items_ids[properties.items[0]]; }
              }
              else
              {
                // add to global
                all_selected_items.push(properties.items[0]);
                // add generateID
                all_selected_items_ids[properties.items[0]] = thisNewItem['start']+'-'+thisNewItem['end']+'-'+thisNewItem['group'];
              }
            }
            
            for (var l in all_selected_items)
            {
              if (!timeline.itemsData._data[all_selected_items[l]])
              {
                //alert('Not found old elements!');
                
                // go next
                continue;
                
                // REset this item id (функция update() полностью переназначает все id элементов, а мы возвращаем id обратно)
                //if (all_selected_items_ids[all_selected_items[l]])
                //{
                  //let thisLitemID = all_selected_items_ids[all_selected_items[l]];
                  //delete all_selected_items_ids[all_selected_items[l]];
                  //all_selected_items[l] = getKeyByText(all_selected_items_ids, thisLitemID);
                //}
                //else
                //{
                  // what? bye...
                  //continue;
                //}
              }
              let thisItem = timeline.itemsData._data[all_selected_items[l]];
              let thisGroup = getGroupByID(thisItem['group']);
              // MP (only one)
              if (thisItem && thisItem['className'] && thisItem['className'] == 'expected' && !isEquipmentGroup(thisGroup))
              {
                if (MPcount > 0)
                {
                  delete all_selected_items[l];
                  //if (all_selected_items_ids[all_selected_items[l]]) { delete all_selected_items_ids[all_selected_items[l]]; }
                }
                else
                {
                  // add to data
                  selected_mp.push(thisItem);
                }
                MPcount++;
              }
              // + equip
              //else if (thisItem && thisItem['className'] && thisItem['className'] == 'not_is_guarantee')
              else if (thisGroup && isEquipmentGroup(thisGroup))
              {
                // add to equipment data
                selected_equipment.push(thisItem);
              }
              else
              {
                //cancel selection
                delete all_selected_items[l];
                //if (all_selected_items_ids[all_selected_items[l]]) { delete all_selected_items_ids[all_selected_items[l]]; }
              }
            }
            
            // reindex
            all_selected_items = all_selected_items.filter(val => val);
            
            // REset selection
            timeline.setSelection(all_selected_items);
            
            // hide or show record button
            if (all_selected_items.length > 0)
            {
              $(".tl_record_buttonblock").fadeIn();
            }
            else
              $(".tl_record_buttonblock").fadeOut();
        }
    }
});

timeline.on('doubleClick', function (properties) 
{
  logEvent('doubleClick', properties);
});

// parse GET
function parse_query_string(query) {
  var vars = query.split("&");
  var query_string = {};
  for (var i = 0; i < vars.length; i++) {
    var pair = vars[i].split("=");
    var key = decodeURIComponent(pair[0]);
    var value = decodeURIComponent(pair[1]);
    // If first entry with this name
    if (typeof query_string[key] === "undefined") {
      query_string[key] = decodeURIComponent(value);
      // If second entry with this name
    } else if (typeof query_string[key] === "string") {
      var arr = [query_string[key], decodeURIComponent(value)];
      query_string[key] = arr;
      // If third or later entry with this name
    } else {
      query_string[key].push(decodeURIComponent(value));
    }
  }
  return query_string;
}

var query = window.location.search.substring(1);
var qs = parse_query_string(query);
//console.log(qs);
// set global
if (qs['external_log_record']) {window.external_log_record = qs['external_log_record']}
if (qs['d_ref']) {window.d_ref = qs['d_ref']}
if (qs['date']) {window.date = qs['date']}
if (qs['editable']) {window.editable = qs['editable']}
if (qs['r_ref']) {window.r_ref = qs['r_ref']}
if (qs['u_ref']) {window.u_ref = qs['u_ref']}
if (qs['master_only']) {window.master_only = qs['master_only']}
if (qs['readonly']) {window.readonly = qs['readonly']}


function send_record()
{
    if (!selected_mp || !selected_mp[0]) { alert('Необходимо выбрать Менеджера!'); return false; }
    if (!selected_mp[0]['className'] || selected_mp[0]['className'] != 'expected') { alert('Для записи выбран не размеченный промежуток времени. Такого быть не должно.'); return false; }
    
    let newRecordInfo = {"begin":"", "end":"", "manager": {"ref":"", "name":""}, "equipment": []};
    // set master & time
    let masterName = getMasterName(selected_mp[0]['group']); // MASTER_NAME<BR>WORK_NAME
    let startDate = ISODateString(selected_mp[0]['start']);
    let stopDate = ISODateString(selected_mp[0]['end']);
    newRecordInfo.begin = startDate;
    newRecordInfo.end = stopDate;
    newRecordInfo.manager.ref = selected_mp[0]['group'];
    newRecordInfo.manager.name = masterName.split("<BR>")[0]; // split master name only

    // equipment subarray
    if (selected_equipment && selected_equipment.length > 0)
    {
      let equipmentArr = [];
      for(var g in selected_equipment)
      {
        // forming record array
        equipmentArr.push({
          "ref": selected_equipment[g]['group'],
          "begin": ISODateString(selected_equipment[g]['start']),
          "end": ISODateString(selected_equipment[g]['end']),
        });
      }
      // add equipment
      newRecordInfo.equipment = equipmentArr;
    }

    // send postcom to ones
    logEvent("new_record", newRecordInfo);
}


function update() {

    var editable;

    editable = false;
    if (window.editable == '1') 
    {
        editable = true
    }

    // open load window & set next date
    $("div.tl_msg_overlay").fadeIn("fast");
   //$("div.tl_msg .jrnl_date").text(window.date.replace(' 00:00:00', '')); // add selected date
    $("div.tl_msg").fadeIn("fast");
    console.log(window.external_log_record)
    $.ajax({
        url: 'http://' + window.external_log_record + '/get_sale?d_ref=' + window.d_ref + '&date=' + window.date + '&r_ref=' + window.r_ref + '&u_ref=' + window.u_ref,

        success: function (data) {
            
            document.getElementById('loading').style.display = 'none';
            data_json = JSON.parse(data);
      
            // hide fixed windows
            $("div.tl_msg").fadeOut("fast");
            $("div.tl_msg_overlay").fadeOut("fast");

            // clear old items
            //timeline.setItems([]);
            //timeline.setGroups([]);
            //timeline.destroy();
            //timeline = new vis.Timeline(container, [], {});
      
             // set date
            $("#this_date").val(window.date.replace(" 00:00:00", ""));


            if (data_json.length == 0) 
            {
                timeline.setItems([]);
                timeline.setGroups([]);
                return
            }

            groups = data_json.timeline.groups;

            var _groups = new vis.DataSet();

            _groups.add(groups);

            // master only param
            if (window.master_only && window.master_only == 1)
            {
                // rebuild groups ("Мастер-приёмщик" only)
                var len = _groups.length;
                for (var i in _groups['_data'])
                {
                    if (!isMPGroup(_groups['_data'][i]) && !isEquipmentGroup(_groups['_data'][i]))
                    {
                      delete _groups['_data'][i];
                    }
                }
            }
            _items = data_json.timeline.items;
            items = new vis.DataSet(_items);

            items_test = new vis.DataSet(_items);

            items_unselected = new vis.DataSet(data_json.timeline.items_unselected);
            items_garant = new vis.DataSet(data_json.timeline.items_garant);

            hiddenDates = data_json.timeline.hiddenDates;

            links = data_json.timeline.links;

            var options = {
                orientation: 'top',
                editable: editable,
                groupEditable: false,
                start: window.date.toDateFromDatetime(),
                end: window.date.toDateFromDatetime().setMilliseconds(23 * 60 * 60 * 1000),
                min: window.date.toDateFromDatetime(),
                max: window.date.toDateFromDatetime().setMilliseconds(23 * 60 * 60 * 1000),
                zoomMin: 1000 * 60 * 60 * 4,
                zoomMax: 1000 * 60 * 60 * 24 * 31 * 1,
                type: 'range',
                multiselect: false,
                hiddenDates: hiddenDates,
                showMajorLabels: false,
                margin: { item: -1, axis: -1 },
                tooltip: { followMouse: true, overflowMethod: 'cap' },
                stack: false,
                //autoResize: true,
                //timeAxis: {scale: 'minute', step: 20},
                //tooltip: {followMouse: true, overflowMethod: 'cap'},
            };
            
            // set timeline items
            timeline.setOptions(options);
            timeline.setItems(items);
            timeline.setGroups(_groups);

            document.getElementById('works-wrap').style.display = 'none';
            
            // works
            works = data_json.timeline.works;
            if (works != undefined) 
            {
                document.getElementById('works-wrap').style.display = 'block';
                $("div.items-panel ul.items").empty();

                for (var i in works) {
                    $("div.items-panel ul.items").append(
									
						'<li draggable="true" class="item tooltip" onmouseover="tooltip.pop(this, \''+works[i]['name']+'\')">' + works[i]['name'] + 									
						'<span class="items-work-service" style="display:none;">' + works[i]['service'] + '</span>' +
						'<span class="items-work-ref" style="display:none;">' + works[i]['ref'] + '</span>' +
						'<span class="items-work-num-str" style="display:none;">' + works[i]['num_str'] + '</span>' +
						'<span class="items-work-amount" style="display:none;">' + works[i]['amount'] + '</span>' +
						//'<span class="tooltiptext">' + works[i]['name'] + '</span>'+
									
						//'<span class="tooltip" onmouseover="tooltip.pop(this, \'<h3>Lorem //ipsum</h3>Lorem ipsum dolor sit amet, consectetur adipiscing elit. //Vestibulum in consequat neque, eget tempor ipsum.\')">Hover me</span>' +
						'</li>'
									
					);

                }

                var work_items = document.querySelectorAll('.items .item');

                for (var i = work_items.length - 1; i >= 0; i--) {
                    var work_item = work_items[i];
                    work_item.addEventListener('dragstart', handleDragStart.bind(this), false);
                }
            }
            
            // "all but not all" events
            items.on('*', function (event, properties) {
                item = timeline.itemsData._data[properties.items];
                logEvent(event, item);
            });
            
            // update old selected item
            updateItemsIDs();
        },
        error: function (err) 
        {
            console.log('Error', err);
            if (err.status === 0) {
                //alert('Ошибка загрузки данных');
            }
            else {
                //alert('Ошибка загрузки данных');
            }
        }
    }); 
}

function handleDragStart(event) {
    var dragSrcEl = event.target;

	ones_service_txt = $(event.target).find('.items-work-service').html();
	ones_ref_txt = $(event.target).find('.items-work-ref').html();
	ones_num_str_txt = $(event.target).find('.items-work-num-str').html();
	ones_amount_txt = $(event.target).find('.items-work-amount').html();
					
    event.dataTransfer.effectAllowed = 'move';
    var itemType = "range";
    var item = {
        id: new Date(),
        type: itemType,
        content: event.target.innerHTML.trim(),
						title: {ones_service: ones_service_txt, ones_ref: ones_ref_txt, ones_num_str: ones_num_str_txt, event: 'distr_service', ones_amount: ones_amount_txt}
    };

    //var isFixedTimes = (event.target.innerHTML.split('-')[2] && event.target.innerHTML.split('-')[2].trim() == 'fixed times')
    //if (isFixedTimes) {
    //    item.start = new Date();
    //    item.end = new Date(1000 * 60 * 10 + (new Date()).valueOf());
    //}
    event.dataTransfer.setData("text", JSON.stringify(item));
}

function setSelection(properties) {

    logEvent('select', properties);

    if (window.r_ref != '') {
        
        if (window.readonly != '1')
        {
          // if empty - reload "torecord" selected items
          timeline.setSelection(all_selected_items);
          // show record button
          $(".tl_record_buttonblock").fadeIn();
        }
        
        return;
    }

    var _items = properties.items;

    if (_items.length == 0) {
        timeline.setItems(items);
        
        if (window.readonly != '1')
        {
          // if empty - reload "torecord" selected items
          timeline.setSelection(all_selected_items);
          // show record button
          $(".tl_record_buttonblock").fadeIn();
        }
        
        return;
    }

    var now = new Date().getTime();

    timeline.setItems(items_unselected);

    while (new Date().getTime() < now + 250) {
        /* do nothing */
    }

    var sels = [];

    var i_id = _items[0].slice(0, 32);

    sels = links[i_id];

    timeline.setSelection(sels);

    // hide record button
    $(".tl_record_buttonblock").fadeOut();
}

async function update_client() {

    if (is_garant == '1') {
        timeline.setItems(items_garant)
    }
    else {
        timeline.setItems(items)
    }
}

function stringifyObject(object) {
    if (!object) return;
    var replacer = function (key, value) {
        if (value && value.tagName) {
            return "DOM Element";
        } else {
            return value;
        }
    }
    return JSON.stringify(object, replacer)
}

async function logEvent(event, properties) {

    window.postComMessage('event=' + JSON.stringify(event) + ', ' +
        'properties=' + stringifyObject(properties))

}

String.prototype.toDateFromDatetime = function () {
    var parts = this.split(/[. :]/);
    return new Date(parts[2], parts[1] - 1, parts[0], parts[3], parts[4], parts[5]);
}

function add_test_item() {

    items_test.add(var_item);

    timeline.setItems(items_test);

}

function del_test_item() {

    timeline.setItems(items);

    items_test = new vis.DataSet(_items);

}


/* DRAGGABLE WINDOW */

function dragMoveListener (event) {
  var target = event.target,
      // keep the dragged position in the data-x/data-y attributes
      x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx,
      y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy;

  // translate the element
  target.style.webkitTransform =
  target.style.transform =
    'translate(' + x + 'px, ' + y + 'px)';

  // update the posiion attributes
  target.setAttribute('data-x', x);
  target.setAttribute('data-y', y);
}

// this is used later in the resizing and gesture demos
window.dragMoveListener = dragMoveListener;

interact('.resize-container')
.draggable({
  allowFrom: '.resize-drag h3',
  onmove: window.dragMoveListener,
  restrict: {
    //restriction: 'parent',
    elementRect: { top: 1, left: 0, bottom: 0, right: 1 }
  },
})
.resizable({
  // resize from all edges and corners
  edges: { left: true, right: true, bottom: true, top: true },

  // keep the edges inside the parent
  restrictEdges: {
    outer: 'parent',
    endOnly: true,
  },

  // minimum size
  restrictSize: {
    min: { width: 200, height: 100 },
  },

  inertia: true,
})
.on('resizemove', function (event) {
  var target = event.target,
      x = (parseFloat(target.getAttribute('data-x')) || 0),
      y = (parseFloat(target.getAttribute('data-y')) || 0);

  // update the element's style
  target.style.width  = event.rect.width + 'px';
  target.style.height = event.rect.height + 'px';

  // translate when resizing from top or left edges
  x += event.deltaRect.left;
  y += event.deltaRect.top;

  target.style.webkitTransform = target.style.transform =
      'translate(' + x + 'px,' + y + 'px)';

  target.setAttribute('data-x', x);
  target.setAttribute('data-y', y);
  //target.textContent = Math.round(event.rect.width) + '\u00D7' + Math.round(event.rect.height);
});



function loadRecordNext()
{
  // load fixed window
  $("div.tl_record_overlay").fadeIn("fast", function () {
      $("div.tl_record").fadeIn();
  });
}

// get master name on ref (groups)
function getMasterName(masterRef)
{
  let masterName = '';
  
  for(var i in groups)
  {
    if (groups[i]['id'] == masterRef)
    {
      masterName = groups[i]['content'];// .split("<BR>")[0] + need check onUpdate timeline method
      break;
    }
  }
  
  return masterName;
}

// get group by id
//  id - group id to select
function getGroupByID(id) 
{
  for(var i in groups)
  {
    if (groups[i]['id'] == id)
    {
      return groups[i];
      break;
    }
  }
}


function getItemByText(arr, text) 
{
  for(var i in arr)
  {
    if (arr[i] == text)
    {
      return arr[i];
      break;
    }
  }
  return false;
}

function getKeyByText(arr, text) 
{
  for(var i in arr)
  {
    if (arr[i] == text)
    {
      return i;
      break;
    }
  }
  return false;
}

// это группа мастера приёмщика?
// _mp - vis group array
function isMPGroup(_mp)
{
  // лучше делать проверку по классу (className)
  if (_mp['style'].indexOf('background-color: grey') == -1)
    return false;
  else
    return true;
}

// это группа постов/оборудования?
// _mp - vis group array
function isEquipmentGroup(_equip)
{
  // лучше делать проверку по классу (className)
  if (_equip['style'].indexOf('background-color: #999999;') == -1)
    return false;
  else
    return true;
}

// obj Date -> 21.01.1970
function dateToStringCustom(tdt)
{
  return ('0' + tdt.getDate()).slice(-2)+"."+('0' + (tdt.getMonth()+1)).slice(-2)+"."+tdt.getFullYear()+" 00:00:00";
}

function printDateFromISO(iso_date) {
  if (iso_date == '0001-01-01T00:00:00') { return ''; }
  
  let tdt = new Date(iso_date);
  return ('0' + tdt.getDate()).slice(-2)+"."+('0' + (tdt.getMonth()+1)).slice(-2)+"."+tdt.getFullYear()+" "+('0' + tdt.getHours()).slice(-2)+":"+('0' + tdt.getMinutes()).slice(-2);
}

// print ISO string from object
function ISODateString(d) 
{
  if (typeof yourVariable !== 'object') { d = new Date(d); }
  
  function pad(n) {return n<10 ? '0'+n : n}
  return d.getFullYear()+'-'
       + pad(d.getMonth()+1)+'-'
       + pad(d.getDate())+'T'
       + pad(d.getHours())+':'
       + pad(d.getMinutes())+':'
       + pad(d.getSeconds())//+'Z'
}

// get first elemet in array
function first(p){for(var i in p)return p[i];}

// show loading 
function startLoading() 
{
  // open load window & set next date
  $("div.tl_msg_overlay2").fadeIn("fast");
  $("div.tl_msg2").fadeIn("fast");
}

// hide loading 
function stopLoading() 
{
  // hide fixed windows
  $("div.tl_msg2").fadeOut("fast");
  $("div.tl_msg_overlay2").fadeOut("fast");
}



update();


$(function() {

  $("span.date_prev").click(function() {
    // clear
    clearRecordSelection();
    // load new page
    var tpattern = /(\d{2})\.(\d{2})\.(\d{4})/;
    var tdt = new Date(window.date.replace(tpattern,'$3-$2-$1'));
    tdt.setDate(tdt.getDate() - 1);
    window.date = dateToStringCustom(tdt);
    update();
  });

  $("span.refrash").click(function() {
     clearRecordSelection();
     update();
  });

  $("span.date_next").click(function() {
    // clear
    clearRecordSelection();
    // load new page
    var tpattern = /(\d{2})\.(\d{2})\.(\d{4})/;
    var tdt = new Date(window.date.replace(tpattern,'$3-$2-$1'));
    tdt.setDate(tdt.getDate() + 1);
    window.date = dateToStringCustom(tdt);
    update();
  });
  
  $(".tl_record_overlay, .ri-button.no").click(function () {
    if (!$(this).hasClass("blocked"))
    {
      // hide fixed window
      $("div.tl_record").fadeOut("fast", function () {
          $("div.tl_record_overlay").fadeOut("fast");
      });
    }
  });
  
  // read 
  $(".tl_record_button").click(function () {
    // check master isset and expected className
    

    if (!selected_mp || !selected_mp[0]) { alert('Необходимо выбрать Менеджера'); return false; }
    if (!selected_mp[0]['className'] || selected_mp[0]['className'] != 'expected') { alert('Для записи выбран не размеченный промежуток времени. Такого быть не должно.'); return false; }

    //$("div.tl_msg_overlay").show();
    //$("div.tl_msg").show();

    let newRecordInfo = {"begin":"", "end":"", "manager": {"ref":"", "name":""}, "equipment": []};
    // set master & time
    let masterName = getMasterName(selected_mp[0]['group']); // MASTER_NAME<BR>WORK_NAME
    let startDate = ISODateString(selected_mp[0]['start']);
    let stopDate = ISODateString(selected_mp[0]['end']);
    newRecordInfo.begin = startDate;
    newRecordInfo.end = stopDate;
    newRecordInfo.manager.ref = selected_mp[0]['group'];
    newRecordInfo.manager.name = masterName.split("<BR>")[0]; // split master name only

    // equipment subarray
    if (selected_equipment && selected_equipment.length > 0)
    {
      let equipmentArr = [];
      for(var g in selected_equipment)
      {
        // forming record array
        equipmentArr.push({
          "ref": selected_equipment[g]['group'],
          "begin": ISODateString(selected_equipment[g]['start']),
          "end": ISODateString(selected_equipment[g]['end']),
        });
      }
      // add equipment
      newRecordInfo.equipment = equipmentArr;
    }

    // send postcom to ones
    logEvent("new_record", newRecordInfo);
    
  });
  
  // clear selected action
  $(".tl_clearselected_button").click(function () {
    clearRecordSelection();
  });
  
});

var picker = new Pikaday({
    field: document.getElementById('this_date'),
    format: 'DD.MM.YYYY',
    onSelect: function() {
        // clear
        clearRecordSelection();
        // load new page
        var tdt = new Date(this.getMoment().format('YYYY-MM-DD'));
        window.date = dateToStringCustom(tdt);
        update();
        //console.log(this.getMoment().format('Do MMMM YYYY'));
    }
});

// синхронизиует все выбранные visjs id со внутренним списком сопоставлений (generatedID)
function updateItemsIDs()
{
  //all_selected_items_ids = {};
  // generate timeID
  for (var i in timeline.itemsData._data)
  {
    all_selected_items_ids[i] = timeline.itemsData._data[i]['start']+'-'+timeline.itemsData._data[i]['end']+'-'+timeline.itemsData._data[i]['group'];
  }
  // update IDs
  for (var l in all_selected_items)
  {
    if (!timeline.itemsData._data[all_selected_items[l]] && all_selected_items_ids[all_selected_items[l]]) // only not founds elements
    {
      let thisLitemID = all_selected_items_ids[all_selected_items[l]]; // save old selected generatedID
      delete all_selected_items_ids[all_selected_items[l]]; // delete old selected item
      all_selected_items[l] = getKeyByText(all_selected_items_ids, thisLitemID); // reset new selected item
    }
  }
  // reset selection
  timeline.setSelection(all_selected_items);
  
  //clear unused generatedID
  let isUsedItem;
  for (var j in all_selected_items_ids)
  {
    isUsedItem = false;
    for (var u in all_selected_items)
    {
      if (all_selected_items[u] == j) { isUsedItem = true; }
    }
    if (isUsedItem != true) { delete all_selected_items_ids[j]; }
  }
  
}

function clearRecordSelection()
{
    selected_mp = [];
    selected_equipment = [];
    all_selected_items = [];
    all_selected_items_ids = {};
    timeline.setSelection(all_selected_items);
    $(".tl_record_buttonblock").fadeOut();
}

function send_socket()
{
  if (socket)
  {
    // send d_ref to ws server
    socket.send(window.d_ref);
  }
  else
  {
    alert('Не найдено WS соединение для отправки d_ref.');
  }
}


/* WS */

var socket = new WebSocket("ws://192.168.5.134:2033/");

//socket.send("Test message");

socket.onopen = function() {
  console.log("Соединение установлено.");
  
  // send d_ref to ws server
  socket.send(window.d_ref);
};

socket.onclose = function(event) {
  console.log('Соединение закрыто');
  console.log('Код: ' + event.code + ' причина: ' + event.reason);
};

socket.onmessage = function(event) {
  
  console.log("Получены данные " + event.data);
  let sdata = JSON.parse(event.data);
  
  // update timeline on similar date and d_ref
  if (sdata.date.substr(0,10) == window.date.substr(0,10) && sdata.d_ref == window.d_ref.toUpperCase())
  {
    //clearRecordSelection();
    update();
    console.log("Timeline is updated (websocket onmessage)");
  }
  
};

socket.onerror = function(error) {
  console.log("Ошибка " + error.message);
  console.log(error);
};







