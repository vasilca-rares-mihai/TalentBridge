package com.example.myapplication.ui.challenge.challengeInfo

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.PickVisualMediaRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.annotation.OptIn
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.media3.common.MediaItem
import androidx.media3.common.util.UnstableApi
import androidx.media3.datasource.DefaultHttpDataSource
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.exoplayer.source.ProgressiveMediaSource
import androidx.media3.ui.PlayerView
import com.example.myapplication.data.model.Challenge
import com.example.myapplication.ui.theme.background_color
import com.example.myapplication.ui.theme.button_color
import com.example.myapplication.ui.theme.button_text_color
import com.example.myapplication.ui.theme.card_color

@OptIn(UnstableApi::class)
@Composable
fun ChallengeInfoScreen(token: String, challengeInfoViewModel: ChallengeInfoViewModel, challenge: Challenge?, modifier: Modifier = Modifier) {
    val context = LocalContext.current
    var selectedUri by remember { mutableStateOf<Uri?>(null) }

    val statusMessage = challengeInfoViewModel.uploadStatus
    val videoUrl = challengeInfoViewModel.processedVideoUrl

    LaunchedEffect(challenge?.id_challenge) {
        challengeInfoViewModel.clearVideoState()
    }

    val exoPlayer = remember {
        ExoPlayer.Builder(context).build().apply {
            repeatMode = ExoPlayer.REPEAT_MODE_ONE
        }
    }

    val launcher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.PickVisualMedia()
    ) { uri: Uri? ->
        if (uri != null) selectedUri = uri
    }

    LaunchedEffect(videoUrl) {
        videoUrl?.let { url ->
            val dataSourceFactory = DefaultHttpDataSource.Factory()
                .setDefaultRequestProperties(mapOf("Authorization" to "Bearer $token"))

            val mediaSource = ProgressiveMediaSource.Factory(dataSourceFactory)
                .createMediaSource(MediaItem.fromUri(url))

            exoPlayer.setMediaSource(mediaSource)
            exoPlayer.prepare()
            exoPlayer.playWhenReady = true
        }
    }

    LaunchedEffect(selectedUri) {
        selectedUri?.let { uri ->
            challenge?.let {
                challengeInfoViewModel.loadChallengeInfo(context, token, it, uri)
                selectedUri = null
            }
        }
    }

    DisposableEffect(Unit) {
        onDispose { exoPlayer.release() }
    }


    Box(modifier = Modifier.fillMaxSize().background(background_color)) {
        Column(modifier = Modifier.padding(vertical = 60.dp, horizontal = 16.dp).fillMaxWidth()) {

            Card(modifier = Modifier.fillMaxWidth(), elevation = CardDefaults.cardElevation(2.dp), colors = CardDefaults.cardColors(containerColor = card_color)) {
                Column(modifier = Modifier.padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp) ) {

                    if (challenge != null) {
                        Text(
                            text = "Challenge: ${challenge.challenge_name}",
                            style = MaterialTheme.typography.headlineMedium,
                            fontWeight = FontWeight.ExtraBold
                        )
                        Text(
                            text = "Unit: ${challenge.unit_of_measure}",
                            style = MaterialTheme.typography.bodyMedium
                        )
                        Text(
                            text = "Info: ${challenge.info}",
                            style = MaterialTheme.typography.bodyMedium
                        )

                        Divider(modifier = Modifier.padding(vertical = 8.dp))

                        if (videoUrl != null) {
                            Text(text = "Analyzed Result:", fontWeight = FontWeight.Bold)
                            Surface(
                                modifier = Modifier.fillMaxWidth().height(250.dp),
                                shape = MaterialTheme.shapes.medium,
                                color = androidx.compose.ui.graphics.Color.Black
                            ) {
                                AndroidView(
                                    factory = { ctx ->
                                        PlayerView(ctx).apply {
                                            player = exoPlayer
                                            useController = true
                                        }
                                    }, modifier = Modifier.fillMaxSize()
                                )
                            }
                        }

                        if (statusMessage.isNotEmpty()) {
                            Text(
                                text = statusMessage,
                                color = MaterialTheme.colorScheme.primary,
                                fontWeight = FontWeight.Medium
                            )
                        }
                        Spacer(modifier = Modifier.weight(1f))

                        Button(
                            onClick = {launcher.launch(PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.VideoOnly))},
                            colors = ButtonDefaults.buttonColors(containerColor = button_color,
                                contentColor = button_text_color),
                            modifier = Modifier.fillMaxWidth().height(50.dp)
                        ) {
                            Text("SELECT VIDEO")
                        }

                        val isVideoUploaded = statusMessage.contains("successful")

                        Button(
                            onClick = {challengeInfoViewModel.start_analysis(token,challenge.id_challenge)},
                            enabled = isVideoUploaded,
                            modifier = Modifier.fillMaxWidth().height(50.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = button_color,
                                contentColor = button_text_color)

                        ) {
                            Text("START ANALYSIS")
                        }
                    } else {
                        Text("Loading challenge data...")
                    }
                }
            }
        }
    }
}