/**
 * Created by john on 8/21/14.
 */

/*
 * directory-tree conditioner, works on .tree & associated classes
 */
$(window).load(function() {
    $(function () {
        // decorate parent <ul>s
        $('.tree li:has(ul)').addClass('parent_li').find('i.tree-folder').attr('title', 'Collapse this branch');
        // handler for +/- fold/unfold icon buttons
        $('.tree li.parent_li i.tree-folder').on('click', function (e) {
            var children = $(this).closest('li.parent_li').find(' > ul > li');
            if (children.is(":visible")) {
                children.hide('fast');
                $(this).attr('title', 'Expand').addClass('fa-plus-square-o').removeClass('fa-minus-square-o');
            } else {
                children.show('fast');
                $(this).attr('title', 'Collapse').addClass('fa-minus-square-o').removeClass('fa-plus-square-o');
            }
            e.stopPropagation();
        });
        // handler for tag identifiers
        $('.tree span[tag]').on('click', function (e) {
            $('#thread-list').load('/threadlist/' + $(this).attr('tag'), function() {
                var hoverPromise = null;
                //  add hide/show handler for clicks on item links
                $('#thread-list .item-link').on('click', function (e) {
                    if (hoverPromise)
                        hoverPromise.clear();
                    var item = $(this).closest('div').find('.item-body');
                    if (item.is(":visible"))
                        item.hide('fast');
                    else
                        item.show('fast');
                    e.stopPropagation();
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
                        item.show('fast');
                    }
                    e.stopPropagation();
                }, function(e) {
                    var item = $(this).closest('div').find('.item-body');
                    if (item.is(":visible"))
                        // delay close giving time for a hover over item to keep it open
                        hoverPromise = $.timeout(500).done(function() {
                            item.hide('fast');
                        });
                });
            });
            $('.tree span[tag]').removeClass("selected-feed");
            $(this).addClass("selected-feed");
            e.stopPropagation();
        });
    });
});
