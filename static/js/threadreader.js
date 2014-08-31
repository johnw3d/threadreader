/**
 * Created by john on 8/21/14.
 */

/*
 * directory-tree conditioner, works on .tree & associated classes
 */

var treeState = { }

function reopenTree() {
    // reopen newly-installed tree-directory from treeState + ensure new-feed is visible if supplied
    $('.tree[new_feed]').each(function() {
        var new_feed = $(this).attr('new_feed');
        var parent_li = $('.tree span[tag="' + new_feed + '"]').parents('li.parent_li');
        parent_li.each(function() {
            // set open state of all parents of new-feed in treeState
            var parent_tag = $(this).find('> span > span[tag]').attr('tag');
            treeState[parent_tag] = true;
        });
    })
    for (tag in treeState)
        if (treeState[tag]) {
            var parent_li = $('.tree span[tag="' + tag + '"]').closest('li.parent_li');
            parent_li.find(' > ul > li').show();
            parent_li.find('> span > i.tree-folder').attr('title', 'Collapse')
                .addClass('fa-minus-square-o')
                .removeClass('fa-plus-square-o');
        }
}

function selectThread(tag) {
    // selected thread for given tag, reveal it in directory, load into threadlist
    // first reveal in directory
    var tag_span = $('.tree span[tag="' + tag + '"]');
    var parent_li = tag_span.parents('li.parent_li');
    var children = parent_li.find(' > ul > li');
    children.show('fast');
    parent_li.each(function() {
        // record open state of all parents in treeState
        var parent_tag = $(this).find('> span > span[tag]').attr('tag');
        treeState[parent_tag] = true;
    });
    // flip to close handle
    parent_li.find('i.tree-folder').attr('title', 'Collapse').addClass('fa-minus-square-o').removeClass('fa-plus-square-o');
    // display thread
    displayThread(tag);
}

function displayThread(tag) {
    // open thread in main-col
    $('#main-col').load('/threadlist/' + encodeURIComponent(tag), function() {
        var hoverPromise = null;
        //  add hide/show handler for clicks on item links
        $('#thread-list .item-link').on('click', function (e) {
            if (hoverPromise)
                hoverPromise.clear();
            var parent_div = $(this).closest('div');
            var item = parent_div.find('.item-body');
            if (item.is(":visible")) {
                parent_div.find('.item-header').hide('fast');
                item.hide('fast');
            }
            else {
                parent_div.find('.item-header').show('fast');
                item.show('fast');
            }
            e.preventDefault();
        });
        // hover over item clears any pending hover-pad closes
        $('#thread-list .item-link').hover(function (e) {
            if (hoverPromise)
                hoverPromise.clear();
        });
        // add hover-reveal handler for item
        $('#thread-list .hover-pad').hover(function (e) {
            var item = $(this).closest('div').find('.item-body');
            if (!item.is(":visible")) {
                // open if we are over pad for >= 250ms
                hoverPromise = $.timeout(250).done(function() {
                    item.show('fast');
                })
            }
            e.stopPropagation();
        }, function(e) {
            if (hoverPromise)
                hoverPromise.clear();
            var item = $(this).closest('div').find('.item-body');
            if (item.is(":visible"))
                // delay close giving time for a hover over item link to keep it open
                hoverPromise = $.timeout(500).done(function() {
                    item.hide('fast');
                });
        });
        // add new item tags
        $('#thread-list .add-item-tags').on('click', function (e) {
            var input = $(this).siblings('input[name=tags]');
            var item_id = $(this).attr("item");
            $('#directory-tree').load('/itemtag/' + item_id, {tags: input.val()}, function() {
                input.val('');
                $('#thread-sel-' + item_id).load('/threadselector/item/' + item_id);
                prepareDirectoryTree();
                reopenTree();
            });
            e.preventDefault();
        });
        // associated threads selector
        $('#thread-list select[name=threads]').change(function (e) {
            // select thread for this option's tag
            var tag = $(this).val();
            selectThread(tag);
            e.preventDefault();
        });
    });
    $('.tree span[tag]').removeClass("selected-feed");
    $('.tree span[tag="' + tag + '"]').addClass("selected-feed");
}

function prepareDirectoryTree() {
    // decorate parent <ul>s
    $('.tree li:has(ul)').addClass('parent_li').find('i.tree-folder').attr('title', 'Expand this branch');
    // handler for +/- fold/unfold icon buttons
    $('.tree li.parent_li i.tree-folder').on('click', function (e) {
        var parent_li = $(this).closest('li.parent_li');
        var children = parent_li.find(' > ul > li');
        var tag = parent_li.find('span[tag]').attr('tag');
        if (children.is(":visible")) {
            children.hide('fast');
            treeState[tag] = false;
            $(this).attr('title', 'Expand').addClass('fa-plus-square-o').removeClass('fa-minus-square-o');
        } else {
            children.show('fast');
            treeState[tag] = true;
            $(this).attr('title', 'Collapse').addClass('fa-minus-square-o').removeClass('fa-plus-square-o');
        }
        e.stopPropagation();
    });

    // handler for tag identifiers in the directory, click to display tag's thread
    $('.tree span[tag]').on('click', function (e) {
        var tag = $(this).attr('tag');
        displayThread(tag);
    });
}

$(window).load(function() {
    $(function () {
        // format tag directory
        prepareDirectoryTree();
        // add-feed handlers  (should this be in separate doc.ready wrapper?)
        $('#add-feed-button').on('click', function(e) {
            $('.tree span[tag]').removeClass("selected-feed");
            $('#main-col').load('/addfeed/', function() {
                $('#add-feed #add-feed-form').on('submit', function(e) {
                    $('#add-feed-submit').html('adding feed...').addClass('add-feed-alert');
                    // send new feed to server & reload directory tree
                    $('#directory-tree').load('/addfeed/directory/', $(this).serializeArray(), function() {
                        $('#add-feed-submit').html('Done, add another feed').removeClass('add-feed-alert');
                        $('#add-feed-url').val('');
                        prepareDirectoryTree();
                        reopenTree();
                    });
                    e.preventDefault();
                });
            });
        });
    });
});


/*
 * add-feed handlers
 */

