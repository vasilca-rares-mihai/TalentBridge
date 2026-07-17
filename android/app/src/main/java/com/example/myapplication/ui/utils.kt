package com.example.myapplication.ui

import android.util.Base64
import org.json.JSONObject

fun getUserIdFromToken(token: String): Int {
    try {
        val split = token.split(".")
        if (split.size < 2) return -1

        val payloadBase64 = split[1]
        val payloadString = String(Base64.decode(payloadBase64, Base64.URL_SAFE))

        val jsonObject = JSONObject(payloadString)

        return jsonObject.getString("sub").toInt()


    } catch (e: Exception) {
        e.printStackTrace()
        return -1
    }
}

fun getRoleFromToken(token: String): String {
    try {
        val split = token.split(".")
        if (split.size < 2) return ""

        val payloadBase64 = split[1]
        val payloadString = String(Base64.decode(payloadBase64, Base64.URL_SAFE))

        val jsonObject = JSONObject(payloadString)

        return jsonObject.getString("role")

    } catch (e: Exception) {
        e.printStackTrace()
        return ""
    }
}

fun getEmailFromToken(token: String): String {
    try {
        val split = token.split(".")
        if (split.size < 2) return ""

        val payloadBase64 = split[1]
        val payloadString = String(android.util.Base64.decode(payloadBase64, android.util.Base64.URL_SAFE))

        val jsonObject = org.json.JSONObject(payloadString)

        return jsonObject.getString("email")

    } catch (e: Exception) {
        e.printStackTrace()
        return ""
    }
}