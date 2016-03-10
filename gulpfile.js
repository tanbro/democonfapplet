var gulp = require('gulp'),
    webserver = require('gulp-webserver');;

gulp.task('webserver', function () {
    gulp.src('webapp')
        .pipe(webserver({
            livereload: true,
            directoryListing: {
                enable: false,
                path: 'webapp'
            },
            open: true
        }));
});

