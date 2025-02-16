package com.example.washwise

import android.graphics.BitmapFactory
import androidx.camera.core.ImageProxy
import coil3.Bitmap
import java.nio.ByteBuffer
import android.graphics.Matrix

fun ImageProxyToBitmap(image : ImageProxy):Bitmap?{
    val buffer: ByteBuffer = image.planes[0].buffer
    val bytes = ByteArray(buffer.remaining())
    buffer.get(bytes)
    val bitmap = BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
    val rotation = image.imageInfo.rotationDegrees
    return if (rotation != 0) {
        val matrix = Matrix().apply { postRotate(rotation.toFloat()) }
        Bitmap.createBitmap(
            bitmap, 0, 0, bitmap.width, bitmap.height, matrix, true
        )
    } else {
        bitmap
    }

}