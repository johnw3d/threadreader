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
            $('#thread-list').load('/threadlist/' + $(this).attr('tag'));
            e.stopPropagation();
        });

    });
});

