package com.example.myapplication.ui.challenge.challengeInfo

import android.app.Activity
import android.content.Context
import android.content.ContextWrapper
import android.content.pm.ActivityInfo
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
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
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

// helper: gaseste Activity-ul din Context (pt blocarea orientarii in fullscreen)
private fun Context.findActivity(): Activity? {
    var ctx = this
    while (ctx is ContextWrapper) {
        if (ctx is Activity) return ctx
        ctx = ctx.baseContext
    }
    return null
}

@OptIn(UnstableApi::class)
@Composable
fun ChallengeInfoScreen(token: String, challengeInfoViewModel: ChallengeInfoViewModel, challenge: Challenge?, modifier: Modifier = Modifier) {
    val context = LocalContext.current
    var selectedUri by remember { mutableStateOf<Uri?>(null) }
    var isFullscreen by remember { mutableStateOf(false) }   // <-- stare fullscreen

    val statusMessage = challengeInfoViewModel.uploadStatus
    val videoUrl = challengeInfoViewModel.processedVideoUrl

    LaunchedEffect(challenge?.id_challenge) {
        challenge?.let {
            challengeInfoViewModel.checkSavedVideo(context, it.id_challenge, token)
        }
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
        if (!videoUrl.isNullOrEmpty()) {
            val dataSourceFactory = DefaultHttpDataSource.Factory()
                .setDefaultRequestProperties(mapOf("Authorization" to "Bearer $token"))

            val mediaSource = ProgressiveMediaSource.Factory(dataSourceFactory)
                .createMediaSource(MediaItem.fromUri(videoUrl))

            exoPlayer.setMediaSource(mediaSource)
            exoPlayer.prepare()
            exoPlayer.playWhenReady = true
        } else {
            exoPlayer.stop()
            exoPlayer.clearMediaItems()
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

            Card(
                modifier = Modifier.fillMaxWidth(),
                elevation = CardDefaults.cardElevation(2.dp),
                colors = CardDefaults.cardColors(containerColor = card_color)
            ) {
                Column(modifier = Modifier.padding(20.dp).verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(12.dp)) {

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

                        if (!videoUrl.isNullOrEmpty()) {
                            Text(text = "Analyzed Result:", fontWeight = FontWeight.Bold)
                            // player INLINE (doar cand NU suntem in fullscreen)
                            if (!isFullscreen) {
                                Surface(
                                    modifier = Modifier.fillMaxWidth().height(250.dp),
                                    shape = MaterialTheme.shapes.medium,
                                    color = Color.Black
                                ) {
                                    AndroidView(
                                        factory = { ctx ->
                                            PlayerView(ctx).apply {
                                                player = exoPlayer
                                                useController = true
                                                setFullscreenButtonClickListener { isFullscreen = true }
                                            }
                                        },
                                        update = { it.player = exoPlayer },
                                        modifier = Modifier.fillMaxSize()
                                    )
                                }
                            }
                        }

                        // --- REZUMAT ANALIZA (sub video) ---
                        val summary = challengeInfoViewModel.analysisSummary
                        if (summary != null) {
                            Surface(
                                modifier = Modifier.fillMaxWidth(),
                                shape = MaterialTheme.shapes.medium,
                                color = MaterialTheme.colorScheme.surfaceVariant
                            ) {
                                Column(
                                    modifier = Modifier.padding(14.dp),
                                    verticalArrangement = Arrangement.spacedBy(4.dp)
                                ) {
                                    Text("Rezultatul analizei", fontWeight = FontWeight.Bold)
                                    if (summary.total != null) {
                                        Text("Repetari corecte: ${summary.correct ?: 0} / ${summary.total}")
                                    } else if (summary.reps != null) {
                                        Text("Repetari: ${summary.reps}")
                                    }
                                    summary.accuracy?.let { Text("Acuratete: $it%") }
                                    summary.bestDistanceM?.let { Text("Distanta: $it m") }
                                    summary.speedMs?.let { Text("Viteza: $it m/s") }
                                    val mistakes = summary.mistakes ?: emptyMap()
                                    if (mistakes.isNotEmpty()) {
                                        Text("Greseli:", fontWeight = FontWeight.Medium)
                                        mistakes.forEach { (name, count) ->
                                            Text(
                                                "• ${name.replace('_', ' ')}: $count",
                                                color = if (count > 0) Color(0xFFD32F2F)
                                                        else MaterialTheme.colorScheme.onSurfaceVariant
                                            )
                                        }
                                    }
                                }
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
                            onClick = { launcher.launch(PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.VideoOnly)) },
                            colors = ButtonDefaults.buttonColors(
                                containerColor = button_color,
                                contentColor = button_text_color
                            ),
                            modifier = Modifier.fillMaxWidth().height(50.dp)
                        ) {
                            Text("SELECT VIDEO")
                        }

                        val isVideoUploaded = challengeInfoViewModel.hasRawVideo

                        Button(
                            onClick = { challengeInfoViewModel.start_analysis(context, token, challenge.id_challenge) },
                            enabled = isVideoUploaded,
                            modifier = Modifier.fillMaxWidth().height(50.dp),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = button_color,
                                contentColor = button_text_color
                            )
                        ) {
                            Text("START ANALYSIS")
                        }
                    } else {
                        Text("Loading challenge data...")
                    }
                }
            }
        }

        // player FULLSCREEN (dialog peste tot ecranul, landscape)
        if (isFullscreen) {
            val activity = context.findActivity()
            Dialog(
                onDismissRequest = { isFullscreen = false },
                properties = DialogProperties(usePlatformDefaultWidth = false)
            ) {
                DisposableEffect(Unit) {
                    val original = activity?.requestedOrientation
                    activity?.requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_SENSOR_LANDSCAPE
                    onDispose {
                        activity?.requestedOrientation = original ?: ActivityInfo.SCREEN_ORIENTATION_UNSPECIFIED
                    }
                }
                Box(modifier = Modifier.fillMaxSize().background(Color.Black)) {
                    AndroidView(
                        factory = { ctx ->
                            PlayerView(ctx).apply {
                                player = exoPlayer
                                useController = true
                                setFullscreenButtonClickListener { isFullscreen = false }
                            }
                        },
                        update = { it.player = exoPlayer },
                        modifier = Modifier.fillMaxSize()
                    )
                }
            }
        }
    }
}