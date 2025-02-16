package com.example.washwise

import android.content.pm.PackageManager
import coil3.compose.rememberAsyncImagePainter
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.core.ImageProxy
import androidx.camera.view.CameraController
import androidx.camera.view.LifecycleCameraController
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Done
import androidx.compose.material3.BottomSheetScaffold
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.rememberBottomSheetScaffoldState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.vectorResource
import androidx.compose.ui.unit.dp
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import coil3.Bitmap
import com.example.washwise.ui.theme.WashWiseTheme

class MainActivity : ComponentActivity() {
    @OptIn(ExperimentalMaterial3Api::class)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        if (!hasCameraPermission()) {
            ActivityCompat.requestPermissions(
                this, arrayOf(CAMERAX_PERMISSION),0)
        }
        setContent {
            WashWiseTheme {
                val controller = remember {
                    LifecycleCameraController(applicationContext).apply {
                        setEnabledUseCases(CameraController.IMAGE_CAPTURE)
                    }
                }
                var capturedImage by remember { mutableStateOf<Bitmap?>(null) }

                val scaffoldState = rememberBottomSheetScaffoldState()
                BottomSheetScaffold(
                    scaffoldState = scaffoldState,
                    sheetPeekHeight = 0.dp,
                    sheetContent = {}) {
                    padding -> Box( // BottomSheetScaffold returns padding to be passed to Box
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(padding)
                    ) { // content inside the box
                        if (capturedImage == null) {
                            ShowCameraPreview(
                                controller = controller,
                                modifier = Modifier.fillMaxSize()
                            )
                            IconButton(
                                onClick = {
                                    controller.cameraSelector =
                                        if (controller.cameraSelector == CameraSelector.DEFAULT_FRONT_CAMERA) {
                                            CameraSelector.DEFAULT_BACK_CAMERA
                                        } else CameraSelector.DEFAULT_FRONT_CAMERA
                                },
                                modifier = Modifier
                                    .padding(16.dp)
                                    .align(Alignment.TopStart)
                            ) {
                                Icon(
                                    imageVector = ImageVector.vectorResource(id = R.drawable.switch_camera),
                                    contentDescription = "Switch Camera"
                                )
                            }
                            IconButton(
                                onClick = {
                                    controller.takePicture(
                                        ContextCompat.getMainExecutor(applicationContext),
                                        object: ImageCapture.OnImageCapturedCallback() {
                                            override fun onCaptureSuccess(image: ImageProxy) {
                                                super.onCaptureSuccess(image)
                                                capturedImage = ImageProxyToBitmap(image)
                                                image.close()
                                            }
                                            override fun onError(exception: ImageCaptureException) {
                                                super.onError(exception)
                                            }

                                        })
                                },
                                modifier = Modifier
                                    .align(Alignment.Center)
                            ) {
                                Icon(
                                    imageVector = ImageVector.vectorResource(id = R.drawable.camera),
                                    contentDescription = "Take Photo"
                                )
                            }
                        } else {
                            ConfirmImage(
                                capturedImage = capturedImage,
                                onConfirm = {},
                                onRetake = { capturedImage = null }
                            )
                        }
                }
                }
            }
        }
    }


    @Composable
    private fun ConfirmImage(capturedImage: Bitmap?, onConfirm:() -> Unit, onRetake:() -> Unit) {
        Box(modifier = Modifier.fillMaxSize()) {
            Image(
                bitmap = capturedImage!!.asImageBitmap(),
                contentDescription = "Image to Confirm",
                modifier = Modifier.fillMaxSize()
            )
            Row(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .padding(0.dp, 30.dp),
                horizontalArrangement = Arrangement.SpaceAround
            ) {
                IconButton(
                    onClick = onConfirm,
                    modifier = Modifier.padding(16.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Done,
                        contentDescription = "Confirm"
                    )
                }
                IconButton(
                    onClick = onRetake,
                    modifier = Modifier.padding(16.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.Close,
                        contentDescription = "Retake"
                    )
                }
            }
        }
    }

    private fun hasCameraPermission(): Boolean {
        return ContextCompat.checkSelfPermission(this, CAMERAX_PERMISSION) == PackageManager.PERMISSION_GRANTED
    }
    companion object {
        private val CAMERAX_PERMISSION = android.Manifest.permission.CAMERA
    }
}