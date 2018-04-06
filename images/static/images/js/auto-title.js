if (!$) {
    $ = django.jQuery;
}

// if empty set the title to the chosen file name
$(document).on('change', '#id_file', function () {
    var $this = $(this), $title = $('#id_title');

    if ($title.val() == "" && $this.get(0).files.length > 0) {
        $title.val($this.get(0).files[0].name);
    }
});
