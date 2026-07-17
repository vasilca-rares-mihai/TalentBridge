package com.example.myapplication.ui.navigation

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Face
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.Icon
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.adaptive.navigationsuite.NavigationSuiteDefaults
import androidx.compose.material3.adaptive.navigationsuite.NavigationSuiteScaffold
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.tooling.preview.PreviewScreenSizes
import com.example.myapplication.ui.theme.MyApplicationTheme
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.myapplication.ui.auth.AuthScreen
import com.example.myapplication.ui.profile.ProfileViewModel
import com.example.myapplication.ui.challenge.challengeAdmin.ChallengeAdminViewModel
import com.example.myapplication.ui.settings.SettingsViewModel
import com.example.myapplication.ui.leaderboard.LeaderboardViewModel
import com.example.myapplication.ui.challenge.challengeList.ChallengeListViewModel
import com.example.myapplication.ui.challenge.challengeInfo.ChallengeInfoViewModel
import com.example.myapplication.ui.fc_search_athlete.SearchViewModel
import com.example.myapplication.ui.getRoleFromToken
import com.example.myapplication.ui.theme.card_color
import com.example.myapplication.ui.trials.TrialViewModel
import com.example.myapplication.ui.watchlist.WatchlistViewModel


class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            MyApplicationTheme {
                RootApp()
            }
        }
    }
}

@Composable
fun RootApp() {
    var currentToken by rememberSaveable {mutableStateOf<String?>(null)}
    if(currentToken == null) {
        AuthScreen(onLoginSuccess = {tokenPrimitDeLaServer -> currentToken = tokenPrimitDeLaServer},
            onAccountCreated = {}
        )
    } else {
        MyApplicationApp(token = currentToken!!, onLogout = { currentToken = null })
    }

}

@PreviewScreenSizes
@Composable
fun MyApplicationApp(profileViewModel: ProfileViewModel = viewModel(), challengeAdminViewModel: ChallengeAdminViewModel = viewModel(), settingsViewModel: SettingsViewModel = viewModel(), searchFCViewModel: SearchViewModel = viewModel(), challengeInfoViewModel: ChallengeInfoViewModel = viewModel(), challengeListViewModel: ChallengeListViewModel = viewModel(), trialViewModel: TrialViewModel = viewModel(), watchlistViewModel: WatchlistViewModel = viewModel(), leaderboardViewModel: LeaderboardViewModel = viewModel(), token: String = "", onLogout: () -> Unit = {}) {
    var currentDestination by rememberSaveable { mutableStateOf(AppDestinations.PROFILE) }
    var role by rememberSaveable{mutableStateOf("")}

    LaunchedEffect(Unit) {
        role = getRoleFromToken(token)
    }
    NavigationSuiteScaffold(
        navigationSuiteColors = NavigationSuiteDefaults.colors(
            navigationBarContainerColor = card_color,
        ),
        navigationSuiteItems = {
            AppDestinations.entries.forEach {
                item(
                    icon = {
                        Icon(
                            imageVector = it.getIcon(role),
                            contentDescription = it.getLabel(role)
                        )
                    },
                    label = { Text(it.getLabel(role)) },
                    selected = it == currentDestination,
                    onClick = { currentDestination = it },
                )
            }
        }
    ) {
        Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
            when (currentDestination) {
                AppDestinations.PROFILE -> {
                    if(role == "athlete") {
                        com.example.myapplication.ui.profile.ProfileAthleteScreen(
                            token = token,
                            profileViewModel = profileViewModel,
                            modifier = Modifier.padding(innerPadding),
                            onLogout = onLogout,
                        )
                    } else if (role == "football_club") {
                        com.example.myapplication.ui.profile.ProfileFootballClubScreen(
                            token = token,
                            profileViewModel = profileViewModel,
                            watchlistViewModel = watchlistViewModel,
                            modifier = Modifier.padding(innerPadding),
                            onLogout = onLogout,
                        )
                    } else if (role == "admin") {

                        com.example.myapplication.ui.profile.ProfileAdminScreen(
                            token = token,
                            profileViewModel = profileViewModel,
                            modifier = Modifier.padding(innerPadding),
                            onLogout = onLogout,
                        )
                    }
                }
                AppDestinations.CHALLENGES -> {
                    if(role == "athlete") {
                        com.example.myapplication.ui.challenge.ChallengeScreen(
                            token = token,
                            challengeListViewModel = challengeListViewModel,
                            challengeInfoViewModel = challengeInfoViewModel,
                            modifier = Modifier.padding(innerPadding)
                        )
                    }else if(role == "football_club") {
                        com.example.myapplication.ui.fc_search_athlete.SearchFootballClubScreen(
                            token = token,
                            searchFCViewModel = searchFCViewModel,
                            watchlistViewModel =  watchlistViewModel,
                            modifier = Modifier.padding(innerPadding)
                        )
                    } else if(role == "admin") {
                        com.example.myapplication.ui.challenge.challengeAdmin.ChallengeAdminScreen(
                            token = token,
                            challengeAdminViewModel = challengeAdminViewModel,
                            modifier = Modifier.padding(innerPadding)
                        )
                    }
                }
                AppDestinations.TRIALS -> {
                    if(role == "athlete") {
                        com.example.myapplication.ui.trials.TrialScreen(
                            token = token,
                            trialViewModel = trialViewModel,
                            profileViewModel = profileViewModel,
                            modifier = Modifier.padding(innerPadding)
                        )
                    }else if(role == "football_club") {
                        com.example.myapplication.ui.trials.TrialFootballClubScreen(
                            token = token,
                            trialViewModel = trialViewModel,
                            watchlistViewModel =  watchlistViewModel,
                            modifier = Modifier.padding(innerPadding)
                        )
                    }else if(role == "admin") {
                    com.example.myapplication.ui.fc_search_athlete.SearchAdminScreen(
                        token = token,
                        searchFCViewModel = searchFCViewModel,
                        modifier = Modifier.padding(innerPadding)
                    )
                    }

                }
                AppDestinations.LEADERBOARD -> {
                    com.example.myapplication.ui.leaderboard.LeaderboardScreen(
                        token = token,
                        leaderboardViewModel = leaderboardViewModel,
                        modifier = Modifier.padding(innerPadding)
                    )
                }
                AppDestinations.SETTINGS -> {
                    com.example.myapplication.ui.settings.SettingsScreen(
                        settingsViewModel = settingsViewModel,
                        token = token,
                        profileViewModel = profileViewModel,
                        onLogout = onLogout,
                        modifier = Modifier.padding(innerPadding)
                    )
                }
            }
        }
    }
}


enum class AppDestinations(
    private val defaultLabel: String,
    private val defaultIcon: ImageVector,
) {
    TRIALS("Trials", Icons.Default.Check),
    CHALLENGES("Challenges", Icons.Default.PlayArrow),
    PROFILE("Profile", Icons.Default.Face),
    SETTINGS("Settings", Icons.Default.Settings),
    LEADERBOARD("Ranking", Icons.Default.Star);

    fun getLabel(role: String): String {
        return if (this == CHALLENGES && role == "football_club") {
            "Athletes"
        } else if (this == TRIALS && role == "admin") {
            "Users"
        } else {

            defaultLabel
        }
    }

    fun getIcon(role: String): ImageVector {
        return if (this == CHALLENGES && role == "football_club") {
            Icons.Default.Person
        } else if (this == TRIALS && role == "admin") {
            Icons.Default.Person
        } else {
            defaultIcon
        }
    }
}

@Composable
fun Greeting(name: String, modifier: Modifier = Modifier) {
    Text(
        text = "Hell22o $name!",
        modifier = modifier
    )
}

@Preview(showBackground = true)
@Composable
fun GreetingPreview() {
    MyApplicationTheme {
        Greeting("Android")
    }
}

