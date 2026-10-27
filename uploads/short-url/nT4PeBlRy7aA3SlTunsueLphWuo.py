from meerkat import reconstruct_data

#reconstruct dataset
reconstruct_data(filename_template='./cbf/%03i.cbf', 
        first_image=1,
        last_image=601,
        reconstruct_in_orthonormal_basis=False,
        maxind=[8,8,8], #the reconstruction will be made for h=-8...8, k=-8...8, l=-8...8
        number_of_pixels=[199, 201, 203], 
        polarization_factor=0.5,
        path_to_XPARM='C:/Users/Gebruiker/Desktop/JH_MH_082_RP8_2/Meerkat', 
        output_filename='reconstruction.h5',
        all_in_memory=True,
        #size_of_cache=100,
        override=True)