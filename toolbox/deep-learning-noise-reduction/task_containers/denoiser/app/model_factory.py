#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Eleftherios Trivizakis
@github: https://github.com/trivizakis
"""
from tensorflow.keras.layers import Conv2D, Activation, BatchNormalization
from tensorflow.keras.layers import Input, Add, Subtract
from tensorflow.keras import Model

def DnCNN(params):    
    input = Input(shape=params["input_shape"],name='input')
    previous = Conv2D(params["kernels"],
                      kernel_size=(3,3),
                      bias_regularizer=params["bias_regularizer"],
                      activity_regularizer=params["activation_regularizer"],
                      kernel_regularizer=params["kernel_regularizer"],
                      kernel_initializer=params["kernel_initializer"],
                      use_bias = True,
                      padding='same',
                      name='conv2d_l1')(input)
    x = Activation('relu',name='act_l1')(previous)
    for i in range(params["layers"]):
        x = Conv2D(params["kernels"],
                   kernel_size=(3,3), 
                 bias_regularizer=params["bias_regularizer"],
                 activity_regularizer=params["activation_regularizer"],
                 kernel_regularizer=params["kernel_regularizer"],
                 kernel_initializer=params["kernel_initializer"],
                 use_bias = True,
                 padding='same',
                 name='conv2d_'+str(i))(x)
        if params["residual"]:
            rescon = Add()([previous,x])
            previous = x
            x = BatchNormalization(axis=-1,momentum=0.0,epsilon=0.0001,name='BN_'+str(i))(rescon)
        else:            
            x = BatchNormalization(axis=-1,momentum=0.0,epsilon=0.0001,name='BN_'+str(i))(x)
        x = Activation('relu',name='act_'+str(i))(x)   
    x = Conv2D(params["input_shape"][2],
               kernel_size=(3,3),
               kernel_regularizer=params["kernel_regularizer"],
               bias_regularizer=params["bias_regularizer"],
               activity_regularizer=params["activation_regularizer"],
               kernel_initializer=params["kernel_initializer"],
               use_bias = True,
               padding='same',
               name='conv2d_l3')(x)
    x = Subtract(name='subtract')([input, x])   
    model = Model(input,x)    
    return model