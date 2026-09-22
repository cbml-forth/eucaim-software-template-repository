#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Eleftherios Trivizakis
@github: https://github.com/trivizakis
"""
import tensorflow as tf


def structural_differences_index(y_true, y_pred):
    max_pixel = 1.0
    ssim_mean = tf.math.reduce_mean(tf.image.ssim(y_true, y_pred, max_val=max_pixel))
    return tf.subtract(1.0, ssim_mean)

class HypesHandler():    
    def add_loss_hypes(hypes):        
        if hypes["loss"] == "MSE":
            hypes["loss"] = tf.keras.losses.MeanSquaredError()
        elif hypes["loss"] == "SDI":
            hypes["loss"] = structural_differences_index
            
        return hypes
            
    def add_optimizer_hypes(hypes):
        if hypes["optimizer"] == "Adam":
            hypes["optimizer"] = tf.keras.optimizers.Adam(learning_rate=hypes["lr"])
        elif hypes["optimizer"] == "SGD":
            hypes["optimizer"] = tf.keras.optimizers.SGD(learning_rate=hypes["lr"])
        
        return hypes
            
    def add_regularizer_hypes(hypes):        
        if hypes["regularizer"] == "l1_l2":
            hypes["kernel_regularizer"] = tf.keras.regularizers.l1_l2(l1=hypes["reg_value"][0], l2=hypes["reg_value"][1])
            hypes["bias_regularizer"] = None#tf.keras.regularizers.l1_l2(l1=hypes["reg_value"][0], l2=hypes["reg_value"][1]),
            hypes["activation_regularizer"] = None#tf.keras.regularizers.l1_l2(l1=hypes["reg_value"][0], l2=hypes["reg_value"][1]),
        elif hypes["regularizer"] == "l1":
            hypes["kernel_regularizer"] = tf.keras.regularizers.l1(hypes["reg_value"][0])
            hypes["bias_regularizer"] = None#tf.keras.regularizers.l1(hypes["reg_value"][0]),
            hypes["activation_regularizer"] = None#tf.keras.regularizers.l1(hypes["reg_value"][0]),
        elif hypes["regularizer"] == "l2":
            hypes["kernel_regularizer"] = tf.keras.regularizers.l2(hypes["reg_value"][0])
            hypes["bias_regularizer"] = None#tf.keras.regularizers.l2(hypes["reg_value"][0]),
            hypes["activation_regularizer"] = None#tf.keras.regularizers.l2(hypes["reg_value"][0]),
            
        return hypes