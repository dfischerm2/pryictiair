$.fn.makeDropzone = function(options = {}) {
    const defaults = {
        icon: 'cloud-upload',
        maxSize: 4,
        acceptedFormats: this.attr('accept') || '*'
    };

    const settings = $.extend({}, defaults, options);

    return this.each(function() {
        const $input = $(this);
        const inputId = $input.attr('id');

        const $wrapper = $('<div/>', {
            class: 'file-upload-wrapper'
        });

        const $dropzone = $(`
            <div class="file-upload-area" id="dropZone_${inputId}">
                <button type="button" class="clear-button" title="Remove file">
                    <i class="fa fa-trash"></i>
                </button>
                <div class="upload-message">
                    <i class="fa fa-${settings.icon} upload-icon"></i>
                    <div class="upload-text">
                        <span class="primary-text">Choose a file</span> or drag it here
                        <span class="file-name"></span>
                    </div>
                    <div class="upload-info">
                        <span class="upload-supports">Supported: ${settings.acceptedFormats}</span>
                        <span class="upload-size">Max: ${settings.maxSize}MB</span>
                    </div>
                </div>
            </div>
        `);

        // Aplicar estructura
        $input.wrap($wrapper);
        $input.before($dropzone);
        $input.css({
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            opacity: 0,
            cursor: 'pointer',
            zIndex: 2
        });

        // Referencias
        const $area = $dropzone;
        const $nameDisplay = $area.find('.file-name');
        const $clearButton = $area.find('.clear-button');

        // Event Handlers para Drag & Drop
        $area.on('dragover dragenter', function(e) {
            e.preventDefault();
            e.stopPropagation();
            $(this).addClass('drag-over');
        });

        $area.on('dragleave dragend drop', function(e) {
            e.preventDefault();
            e.stopPropagation();
            $(this).removeClass('drag-over');
        });

        // Manejar cambios en el input
        $input.on('change', function() {
            const file = this.files[0];
            handleFileSelect(file);
        });

        // Manejar clic en botón de borrar
        $clearButton.on('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            resetUpload();
        });

        function handleFileSelect(file) {
            if (!file) return;

            // Validar tamaño
            if (file.size > settings.maxSize * 1024 * 1024) {
                alert(`El archivo no debe exceder ${settings.maxSize}MB`);
                resetUpload();
                return;
            }

            // Actualizar interfaz
            $nameDisplay.text(file.name);
            $area.addClass('has-file').removeClass('has-error');
            $area.find('.upload-icon')
                .removeClass('fa-cloud-upload')
                .addClass('fa-check-circle');
        }

        function resetUpload() {
            $input.val('');
            $nameDisplay.text('');
            $area.removeClass('has-file has-error');
            $area.find('.upload-icon')
                .removeClass('fa-check-circle')
                .addClass('fa-cloud-upload');
        }
    });
};