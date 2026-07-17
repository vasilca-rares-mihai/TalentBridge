package com.example.myapplication.data.network

import com.example.myapplication.data.network.TalentBridgeApi
import com.google.gson.GsonBuilder
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object RetrofitClient {
    private const val AUTH_URL = "http://10.219.37.138:8000/"
    const val CORE_URL = "http://10.219.37.138:8001/"
    private val customGson = GsonBuilder()
        .setDateFormat("yyyy-MM-dd")
        .create()

    val authApi: TalentBridgeApi by lazy {
        Retrofit.Builder()
            .baseUrl(AUTH_URL)
            .addConverterFactory(GsonConverterFactory.create(customGson))
            .build()
            .create(TalentBridgeApi::class.java)
    }

    val coreApi: TalentBridgeApi by lazy {
        Retrofit.Builder()
            .baseUrl(CORE_URL)
            .addConverterFactory(GsonConverterFactory.create(customGson))
            .build()
            .create(TalentBridgeApi::class.java)
    }
}