module.exports = function(grunt) {

  // Initializing the configuration object
  grunt.initConfig({

    less: {
      development: {
        options: {
          compress: false // true
        },
        files: {
          "./static/dist/everything.css": "./static/less/everything.less"
        }
      }
    },

    copy: {
      main: {
        files: [
          {
            expand: true,
            cwd: 'bower_components/',
            src: [
              'bootstrap/dist/js/bootstrap.min.js',
              'bootstrap/dist/fonts/**',
              'jquery/dist/jquery.min.js',
              'jquery/dist/jquery.min.map',
              'jquery-ui/jquery-ui.min.js',
              'jquery-ui/themes/smoothness/jquery-ui.min.css',
              'jquery-pjax/jquery.pjax.js',
              'font-awesome/fonts/**',
              'html5shiv/dist/html5shiv.min.js',
              'respond/dest/respond.min.js'
            ],
            dest: './static/dist/',
            filter: 'isFile',
            flatten: true
          }
        ]
      }
    },

    clean: ['./static/dist'],

    watch: {
      less: {
        files: ['./static/less/*.less'], //watched files
        tasks: ['less'], //tasks to run
        options: {
          livereload: true
        }
      }
    }
  });

  // Plugin loading
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-contrib-less');
  grunt.loadNpmTasks('grunt-contrib-copy');
  grunt.loadNpmTasks('grunt-contrib-clean');

  // Task definition
  grunt.registerTask('build', ['copy', 'less']);
  grunt.registerTask('default', ['build', 'watch']);
};