(define (apply-painting filename)
   (let* ((image (car (gimp-file-load RUN-NONINTERACTIVE filename filename)))
          (drawable (car (gimp-image-get-active-layer image))))
     (plug-in-gimpressionist RUN-NONINTERACTIVE image drawable "gimpressionist_preset")
     (gimp-file-save RUN-NONINTERACTIVE image drawable filename filename)
     (gimp-image-delete image)))