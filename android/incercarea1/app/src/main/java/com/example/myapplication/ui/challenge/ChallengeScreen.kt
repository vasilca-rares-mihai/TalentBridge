package com.example.myapplication.ui.challenge

import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.example.myapplication.data.model.Challenge
import com.example.myapplication.ui.challenge.challengeInfo.ChallengeInfoScreen
import com.example.myapplication.ui.challenge.challengeInfo.ChallengeInfoViewModel
import com.example.myapplication.ui.challenge.challengeList.ChallengeListScreen
import com.example.myapplication.ui.challenge.challengeList.ChallengeListViewModel

@Composable
fun ChallengeScreen(token: String, challengeListViewModel: ChallengeListViewModel, challengeInfoViewModel: ChallengeInfoViewModel, modifier: Modifier = Modifier) {

    val navController = rememberNavController()
    var selectedChallenge by remember { mutableStateOf<Challenge?>(null) }

    NavHost(navController = navController, startDestination = "challenge_list") {

        composable("challenge_list") {
            ChallengeListScreen(
                token = token,
                challengeListViewModel = challengeListViewModel,
                onChallengeClick = { challenge ->
                    selectedChallenge = challenge
                    navController.navigate("challenge_menu")
                }
            )
        }

        composable("challenge_menu") {
            ChallengeInfoScreen(
                token = token,
                challengeInfoViewModel = challengeInfoViewModel,
                challenge = selectedChallenge
            )
        }
    }
}