package com.example.myapplication.ui.profile

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Badge
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.example.myapplication.data.model.AthleteData
import com.example.myapplication.ui.theme.background_color
import com.example.myapplication.ui.theme.button_color
import com.example.myapplication.ui.theme.button_red_color
import com.example.myapplication.ui.theme.button_text_color
import com.example.myapplication.ui.theme.card_color
import com.example.myapplication.ui.theme.fontTextColor
import com.example.myapplication.ui.watchlist.WatchlistViewModel
import java.text.SimpleDateFormat
import java.util.Locale
import kotlin.collections.component1
import kotlin.collections.component2

@Composable
fun ProfileFootballClubScreen(token: String, profileViewModel: ProfileViewModel, watchlistViewModel: WatchlistViewModel, modifier: Modifier = Modifier, onLogout: () -> Unit) {

    var athleteToShowInfo by remember { mutableStateOf<AthleteData?>(null) }
    var athleteToShowAttributes by remember { mutableStateOf<AthleteData?>(null) }

    LaunchedEffect(Unit) {
        profileViewModel.loadFootballClubData(token)
        watchlistViewModel.get_watchlist(token)
    }

    Box(modifier = Modifier.fillMaxSize().background(background_color)) {
        Column(modifier = modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),verticalArrangement = Arrangement.spacedBy(16.dp)) {
            if (profileViewModel.role == "football_club") {
                val currentFootballClub = profileViewModel.football_club

                Column(modifier = Modifier.fillMaxWidth(),horizontalAlignment = Alignment.CenterHorizontally) {
                    if (currentFootballClub != null) {
                        Text(
                            text = currentFootballClub.name,
                            style = MaterialTheme.typography.headlineMedium,
                            color = fontTextColor,
                            fontWeight = FontWeight.ExtraBold
                        )
                    }
                    Text(
                        text = profileViewModel.email,
                        style = MaterialTheme.typography.bodyMedium,
                        color = fontTextColor
                    )
                    Badge(modifier = Modifier.padding(top = 8.dp), containerColor = Color(0xFF4CAF50)) {
                        Text(
                            text = profileViewModel.role.uppercase(),
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                        )
                    }
                }
                Card(modifier = Modifier.fillMaxWidth(), elevation = CardDefaults.cardElevation(2.dp), colors = CardDefaults.cardColors(containerColor = card_color)) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(
                            text = "Personal information",
                            style = MaterialTheme.typography.titleMedium,
                            modifier = Modifier.padding(bottom = 12.dp),
                            color = fontTextColor,
                        )

                        ProfileInfoRow("Country", "${currentFootballClub?.country}")
                        ProfileInfoRow("Info", "${currentFootballClub?.info} ")
                    }
                }
                Card(modifier = Modifier.fillMaxWidth(), elevation = CardDefaults.cardElevation(2.dp), colors = CardDefaults.cardColors(containerColor = card_color)) {

                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(
                            text = "WatchList",
                            style = MaterialTheme.typography.titleMedium,
                            modifier = Modifier.padding(bottom = 12.dp),
                            color = fontTextColor,
                        )

                        if (watchlistViewModel.athletesWatchlist.isEmpty()) {
                            Text(
                                text = "There are no athletes at the moment.",
                                style = MaterialTheme.typography.bodyMedium,
                                color = fontTextColor,
                                modifier = Modifier.padding(top = 16.dp)
                            )
                        } else {
                            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                                for (i in 0 until watchlistViewModel.athletesWatchlist.size) {
                                    val athlete = watchlistViewModel.athletesWatchlist[i]
                                    Column(modifier = Modifier.padding(8.dp)) {
                                        Row(modifier = Modifier.fillMaxWidth()) {
                                            Text(
                                                text = "${athlete.first_name} ${athlete.second_name}",
                                                color = fontTextColor,
                                                fontWeight = FontWeight.Bold
                                            )

                                            Spacer(modifier = Modifier.weight(1f))
                                            Column(horizontalAlignment = Alignment.End) {
                                                Text(athlete.field_position)
                                            }

                                        }
                                        Row(modifier = Modifier.fillMaxWidth().padding(top = 8.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                            Button(
                                                modifier = Modifier.weight(1f),
                                                onClick = {athleteToShowInfo = athlete},
                                                colors = ButtonDefaults.buttonColors(containerColor = button_color, contentColor = button_text_color)
                                            ) { Text("Info") }

                                            Button(
                                                modifier = Modifier.weight(1f),
                                                onClick = {profileViewModel.get_athlete_attributes(token, athlete.user_id)
                                                    athleteToShowAttributes = athlete
                                                },
                                                colors = ButtonDefaults.buttonColors(containerColor = button_color, contentColor = button_text_color)
                                            ) { Text("Attr") }

                                            val isWatchlisted = watchlistViewModel.athletesWatchlist.any { it.user_id == athlete.user_id }
                                            Button(
                                                onClick = {
                                                    if (isWatchlisted) watchlistViewModel.delete_from_watchlist(token, athlete)
                                                    else watchlistViewModel.add_to_watchlist(token, athlete)
                                                },
                                                colors = ButtonDefaults.buttonColors(containerColor = button_color, contentColor = button_text_color)
                                            ) { Text(if (isWatchlisted) "</3" else "<3") }
                                        }
                                    }

                                }
                                if (athleteToShowInfo != null) {

                                    val currentAthlete = athleteToShowInfo!!
                                    AlertDialog(
                                        onDismissRequest = { athleteToShowInfo = null },
                                        title = { Text("${currentAthlete.first_name} ${currentAthlete.second_name}") },
                                        text = {
                                            Column(horizontalAlignment = Alignment.End) {
                                                ProfileInfoRow("Age", "${currentAthlete.age} ani")
                                                ProfileInfoRow("Height", "${currentAthlete.height}")
                                                ProfileInfoRow("Weight", "${currentAthlete.weight}")
                                                ProfileInfoRow("Weak foot", currentAthlete.weak_foot)
                                                ProfileInfoRow("Date of birth",SimpleDateFormat("dd.MM.yyyy",Locale.getDefault()).format(currentAthlete.date_of_birth))
                                                ProfileInfoRow("Gender", currentAthlete.gender)
                                                ProfileInfoRow("Country", currentAthlete.country)
                                                ProfileInfoRow("Region", currentAthlete.region)
                                                ProfileInfoRow("City", currentAthlete.city)
                                                ProfileInfoRow("Phone number",currentAthlete.phone_number)
                                            } },
                                        confirmButton = {},
                                        dismissButton = {
                                            Button(
                                                onClick = { athleteToShowInfo = null },
                                                colors = ButtonDefaults.buttonColors(
                                                    containerColor = button_color,
                                                    contentColor = button_text_color
                                                )
                                            ) { Text("Back") }
                                        }
                                    )
                                }
                                if (athleteToShowAttributes != null) {
                                    val currentAthlete = athleteToShowAttributes!!
                                    AlertDialog(
                                        onDismissRequest = { athleteToShowAttributes = null },
                                        title = { Text("${currentAthlete.first_name} ${currentAthlete.second_name}") },
                                        text = {
                                            Column(modifier = Modifier.padding(end = 8.dp).verticalScroll(rememberScrollState())) {
                                                AttributeStat("Strength", profileViewModel.attribute?.strength?.toString() ?: "-")
                                                AttributeStat("Jumping", profileViewModel.attribute?.jumping?.toString() ?: "-")
                                                AttributeStat("Acceleration", profileViewModel.attribute?.acceleration?.toString() ?: "-")
                                                AttributeStat("Sprint Speed", profileViewModel.attribute?.sprint_speed?.toString() ?: "-")
                                                AttributeStat("Agility", profileViewModel.attribute?.agility?.toString() ?: "-")
                                                AttributeStat("Balance", profileViewModel.attribute?.balance?.toString() ?: "-")
                                                AttributeStat("Dribbling", profileViewModel.attribute?.dribbling?.toString() ?: "-")
                                                AttributeStat("Finishing", profileViewModel.attribute?.finishing?.toString() ?: "-")
                                            }
                                        },
                                        confirmButton = {},
                                        dismissButton = {
                                            Button(
                                                onClick = { athleteToShowAttributes = null},
                                                colors = ButtonDefaults.buttonColors(containerColor = button_color, contentColor = button_text_color)
                                            ) { Text("Back") }
                                        }
                                    )
                                }
                            }
                        }


                    }
                }

                Button(
                    onClick = { profileViewModel.onLogout(token)
                        onLogout()},
                    modifier = Modifier.fillMaxWidth().height(50.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = button_red_color,
                        contentColor = button_text_color)
                ) {
                    Text("Log out")
                }
            }

            Spacer(modifier = Modifier.height(24.dp))


        }
    }
}