#include <iostream>
#include <opencv2/opencv.hpp>
#include <jpeglib.h>
#include <errno.h>
#include <math.h>	
#include <sys/time.h>
#include <unistd.h>

using namespace cv;
using namespace std;

static unsigned char jpegQuality = 70;

/**
	Print error message and terminate programm with EXIT_FAILURE return code.
	\param s error message to print
*/
static void errno_exit(const char* s)
{
	fprintf(stderr, "%s error %d, %s\n", s, errno, strerror (errno));
	exit(EXIT_FAILURE);
}

/**
	Write image to jpeg file.
	\param img image to write
*/
static void jpegWrite(unsigned char* inputImg, int channels, char* name, int w, int h) {

	unsigned char *img = (unsigned char*)malloc(w*h*channels);
	memcpy(img, inputImg, w*h*channels);

	// From BGR to RGB.
 	if(channels == 3) {
		int i, x, y;
		unsigned char red, blue;
		i=0;
		for(y=0; y < h; y++) {
		    for(x=0; x < w; x++) {
		        blue = (int)img[i];
		        red = (int)img[i+2];
				img[i] = red;
				img[i+2] = blue;
		        i+=3;
		    }
		}
	}

	struct jpeg_compress_struct cinfo;
	struct jpeg_error_mgr jerr;
	
	JSAMPROW row_pointer[1];
	// Try to open file for saving.
	FILE *outfile = fopen( name, "wb");	
	if (!outfile) {
		errno_exit("jpeg");
	}

	// Create jpeg data.
	cinfo.err = jpeg_std_error( &jerr );
	jpeg_create_compress(&cinfo);
	jpeg_stdio_dest(&cinfo, outfile);

	// Set image parameters.
	cinfo.image_width = w;	
	cinfo.image_height = h;
	switch(channels) {
		case 3:
			cinfo.input_components = 3;
			cinfo.in_color_space = JCS_RGB;
			break;
		case 1: 
			cinfo.input_components = 1;
			cinfo.in_color_space = JCS_GRAYSCALE;
			break;
	}

	// Set jpeg compression parameters to default
	jpeg_set_defaults(&cinfo);
	// and then adjust quality setting.
	jpeg_set_quality(&cinfo, jpegQuality, TRUE);

	// Start compress.
	jpeg_start_compress(&cinfo, TRUE);

	// Feed data.
	while (cinfo.next_scanline < cinfo.image_height) {
		row_pointer[0] = &img[cinfo.next_scanline * cinfo.image_width *  cinfo.input_components];
		jpeg_write_scanlines(&cinfo, row_pointer, 1);
	}

	// Finish compression.
	jpeg_finish_compress(&cinfo);

	// Destroy jpeg data.
	jpeg_destroy_compress(&cinfo);

	// Close output file.
	fclose(outfile);

	free(img);
}


int main(int argc, char* argv[]) {

    int i = 0;
	Mat image;
	int num_grab = 1;
	int verbose = 0;
	int device_index = 0;
	char image_name[12] = {0};
	int opt, opt_index;
	
	// put ':' in the starting of the string so that program can distinguish between '?' and ':'
	while((opt = getopt (argc, argv, ":d:n:v")) != -1) {
		switch(opt) {
			case 'd':
				device_index = atoi(optarg);
				break;
			case 'n':
				num_grab = atoi(optarg);
				if(num_grab > 99) {
					num_grab = 99; // This is to avoid buffer overflow on the output file name.
				}				
				break;
			case 'v':
				verbose = 1;
				break;
			case ':': // If an option requires a value and no value is given
				fprintf (stderr, "Option -%c requires an argument.\n", optopt);
				break;
			case '?': // Unrecognized option
				if (isprint (optopt)) {
					fprintf (stderr, "Unknown option `-%c'.\n", optopt);
				} else {
					fprintf (stderr, "Unknown option character `\\x%x'.\n", optopt);
					exit(1);
				}
			default:
				exit(1);
		}
		for (opt_index = optind; opt_index < argc; opt_index++) {
			printf ("Extra arguments: %s\n", argv[opt_index]);
		}
	}
	
	
    VideoCapture camera(device_index);
	if(!camera.isOpened()) {
		std::cout << "Cannot open the video device" << std::endl;
		exit(1);
	}

	//camera.set(CV_CAP_PROP_FRAME_WIDTH, 320);
	//camera.set(CV_CAP_PROP_FRAME_HEIGHT, 240);
	if(verbose) {
		std::cerr << "frame width = " << (int)camera.get(CV_CAP_PROP_FRAME_WIDTH) << std::endl;
		std::cerr << "frame height = " << (int)camera.get(CV_CAP_PROP_FRAME_HEIGHT) << std::endl;
		std::cerr << "fps = " << (int)camera.get(CV_CAP_PROP_FPS) << std::endl;
		std::cerr << "format = " << (int)camera.get(CV_CAP_PROP_FORMAT) << std::endl;
		int ex = static_cast<int>(camera.get(CV_CAP_PROP_FOURCC)); // Get Codec Type- Int form
		// Transform from int to char via Bitwise operators
		char EXT[] = {(char)(ex & 0XFF) , (char)((ex & 0XFF00) >> 8),(char)((ex & 0XFF0000) >> 16),(char)((ex & 0XFF000000) >> 24), 0};
		std::cerr << "Input codec type: " << EXT << std::endl;
	}
	 
	struct timeval start_time, curr_time;	
	int32_t time_diff_us = 0;	
	
    while(num_grab > 0) {
		
		gettimeofday(&start_time, NULL);
		
        camera.read(image);
        if(image.empty()) {
			if(verbose) {
				std::cerr << "frame not grabbed properly" << std::endl;
			}
            return -1;
        }

		sprintf(image_name, "image%.2d.jpg", num_grab);
		jpegWrite((unsigned char*)image.data, image.channels(), image_name, image.cols, image.rows);
		if(verbose) {
			std::cerr << "frame grabbed" << std::endl;
			std::cerr << "nChannels = " << image.channels() << std::endl;		
		}
		
		// Grabbing frequency @ 5 Hz.
		gettimeofday(&curr_time, NULL);
		time_diff_us = (curr_time.tv_sec * 1000000 + curr_time.tv_usec) - (start_time.tv_sec * 1000000 + start_time.tv_usec);		
		if(time_diff_us < 200000) {
			usleep(200000 - time_diff_us);
		}
		
		num_grab--;
		
    }

    return 2;
}
