$.fn.makeDropzone = function(options = {}) {
    const defaults = {
        icon: 'cloud-upload',
        maxSize: 4,
        acceptedFormats: this.attr('accept') || '*'
    };

    const settings = $.extend({}, defaults, options);

    // Convert acceptedFormats to array for validation
    const acceptedExtensions = settings.acceptedFormats === '*'
        ? ['*']
        : settings.acceptedFormats.split(',').map(format =>
            format.trim().toLowerCase().replace('.', '')
          );

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
                    <div class="error-text" style="display: none; color: #fc8181; margin-top: 0.5rem; font-size: 0.875rem;"></div>
                    <div class="upload-info">
                        <span class="upload-supports">Supported: ${settings.acceptedFormats}</span>
                        <span class="upload-size">Max: ${settings.maxSize}MB</span>
                    </div>
                </div>
            </div>
        `);

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

        // References
        const $area = $dropzone;
        const $nameDisplay = $area.find('.file-name');
        const $errorDisplay = $area.find('.error-text');
        const $clearButton = $area.find('.clear-button');
        const $uploadIcon = $area.find('.upload-icon');

        // Event Handlers for Drag & Drop
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

        // Handle drop event
        $area.on('drop', function(e) {
            const file = e.originalEvent.dataTransfer.files[0];
            handleFileSelect(file);
        });

        // Handle input changes
        $input.on('change', function() {
            const file = this.files[0];
            handleFileSelect(file);
        });

        // Handle clear button click
        $clearButton.on('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            resetUpload();
        });

        function validateFileFormat(file) {
            if (acceptedExtensions[0] === '*') return true;

            const fileExtension = file.name.split('.').pop().toLowerCase();
            return acceptedExtensions.includes(fileExtension);
        }

        function handleFileSelect(file) {
            if (!file) return;

            // Reset previous states
            resetStates();

            // Validate size
            if (file.size > settings.maxSize * 1024 * 1024) {
                showError(`The file must not exceed ${settings.maxSize}MB`);
                return;
            }

            // Validate format
            if (!validateFileFormat(file)) {
                const formatsText = acceptedExtensions.map(ext => `.${ext}`).join(', ');
                showError(`Invalid format. Accepted formats: ${formatsText}`);
                return;
            }

            // Success state
            $nameDisplay.text(file.name).show();
            $area.addClass('has-file').removeClass('has-error');
            $uploadIcon
                .removeClass(`fa-${settings.icon} fa-times-circle`)
                .addClass('fa-check-circle');
            $errorDisplay.hide();

            // Trigger success event
            $input.trigger('dropzone:success', [file]);
        }

        function showError(message) {
            $input.val(''); // Clear input
            $nameDisplay.text('').hide();
            $area.removeClass('has-file drag-over').addClass('has-error');
            $uploadIcon
                .removeClass(`fa-${settings.icon} fa-check-circle`)
                .addClass('fa-times-circle');
            $errorDisplay.text(message).show();

            // Trigger error event
            $input.trigger('dropzone:error', [message]);
        }

        function resetStates() {
            $area.removeClass('has-file has-error drag-over');
            $errorDisplay.hide();
            $uploadIcon
                .removeClass('fa-check-circle fa-times-circle')
                .addClass(`fa-${settings.icon}`);
        }

        function resetUpload() {
            $input.val('');
            $nameDisplay.text('').hide();
            resetStates();

            // Trigger reset event
            $input.trigger('dropzone:reset');
        }
    });
};