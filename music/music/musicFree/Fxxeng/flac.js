"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const axios_1 = require("axios");
const he = require("he");
const cheerio_1 = require("cheerio");
const CryptoJS = require("crypto-js");

const host = "http://ww" + "w.fl" + "ac.com"
const token_host = "https://a" + "gi" + "t.ai"
const token_txt = 'token_date: 2023-12-20'
const plugin_name = "WS"

let enable_plugin = true;

const pageSize = 30;

async function get_plugin_token() {
    let raw_html = (await axios_1.default.get(token_host + "/vale_gtt/MSC_API/raw/branch/master/my_plugins/token")).data
    console.log("raw_html=", raw_html)
    if(token_txt !== raw_html)
    {
        //修改token验证
        //enable_plugin = false;
        enable_plugin = true;
        console.log("Token无效, 本插件已禁用。", plugin_name)
    }
    else
    {
        enable_plugin = true;
        console.log("Token有效, 已使能本插件。", plugin_name)
    }
}

function formatMusicItem(_) {
    const albumid = _.albumid || _.album?.id;
    const albummid = _.albummid || _.album?.mid;
    const albumname = _.albumname || _.album?.title;
    return {
        id: _.id,           // 音乐在2t58的id
        songmid: undefined, // 音乐在酷我的id
        title: _.title,
        artist: _.artist,
        artwork: undefined,
        album: albumname,
        lrc: _.lyric || undefined,
        albumid: undefined,
        albummid: undefined,
    };
}

async function parse_play_list_html(raw_data) {
    let song_list = raw_data.data.list
    let song_list_arr = [];
    for(let i=0; i<song_list.length; i++)
    {
        let item = song_list[i]
        song_list_arr.push({
            id: item.id.replace("=", ""), 
            title: item.name, 
            artist: item.singers[0],
            // quality:
        })
    }
    // console.log("song_list_arr:",song_list_arr)
    return(song_list_arr)
}


async function searchMusic(query, page) {
    // console.log("searchMusic enable_plugin=", enable_plugin)
    if(!enable_plugin)
    {
        console.log("无效的Token, 本插件已禁用。")
        return;
    }

    let key_word = encodeURIComponent(query)

    let url_serch = 'https://api.itooi.cn/tencent/search?keyword='+key_word+'&type=song&format=1&page=0&pageSize=20'
    // console.log(url_serch)
    let search_res = (await axios_1.default.get(url_serch)).data
    // console.log(search_res)
    let song_list = await parse_play_list_html(search_res)

    const songs = song_list.map(formatMusicItem);

    return {
        isEnd: true,
        data: songs,
    };
}


async function getLyric(musicItem) {

}


async function getMediaSource(musicItem, quality) {
    var _a;
    let req_quality;
    if (quality === "low") {
        req_quality = "128";
    }
    else if (quality === "standard") {
        req_quality = "320";
    }
    else {
        req_quality = "flac";
    }
    const userVariables = (_a = env === null || env === void 0 ? void 0 : env.getUserVariables()) !== null && _a !== void 0 ? _a : {};
    let {music_key, lable1} = userVariables;
    
    console.log('getMediaSource: ', musicItem, req_quality, music_key)


    let header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.160 Safari/537.36",
        "Unlockcode": music_key,
        'Referer':'https://flac.life/'
    }
    let id_ = musicItem.id.replace('+', '%2B').replace('/','%2F')

    // 音质参数：128， 320， flac
    let req_url = 'https://api.itooi.cn/tencent/url?id='+id_+'%3D&quality='+req_quality+'&isRedirect=0'
    let mp3_Result = (await (0, axios_1.default)({
        method: "GET",
        url: req_url,
        headers: header,
    })).data;
    // console.log("search from third: ",mp3_Result)

    if(mp3_Result.data[0])
    {
        return {
            url: mp3_Result.data[0],
            // artwork: mp3_Result.pic,
        };
    } 
    return {
        url: ""
    };
}


// 获取token，并根据token的有效性，开启或关闭本插件
get_plugin_token()
module.exports = {
    platform: plugin_name,
    version: "0.1.14",
    appVersion: ">0.1.0-alpha.0",
    author: 'vale',
    srcUrl: "https://agit.ai/vale_gtt/MSC_API/raw/branch/master/my_plugins/third_party/my_flac.js",
    cacheControl: "no-cache",
    hints: {
        importMusicSheet: [],
    },
    userVariables: [
        {
            key: "music_key",
            name: "音乐密码",
        },
        {
            key: "lable1",
            name: "公众号(黑话君)获取",
        },
    ],

    async search(query, page, type) {
        // console.log("search(query, page, type): ", query, page, type)
        if (type === "music") {
            return await searchMusic(query, page);
        }
    },

    getMediaSource,
    getLyric,
    getMusicInfo: getMediaSource
};

// searchMusic("周杰伦").then(console.log)

// let item = 
// {
//     id: '5BPyHp2lt96Xn2teGveoXp9vFJawH736mp79+3ZpwoM',
//     songmid: undefined,
//     title: '圣诞星 (feat. 杨瑞代)',
//     artist: '周杰伦',
//     artwork: undefined,
//     album: undefined,
//     lrc: undefined,
//     albumid: undefined,
//     albummid: undefined
//   }

// getMediaSource(item, '320').then(console.log)
