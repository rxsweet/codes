"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const axios_1 = require("axios");
const he = require("he");
const cheerio_1 = require("cheerio");
const CryptoJS = require("crypto-js");
const http = require('http');
const request = require('request');
const https = require('https') //导入https模块
const qs = require("qs")

const host = "http://ww" + "w.2t" + "58.com"
const token_host = "https://a" + "gi" + "t.ai"
const token_txt = 'token_date: 2023-12-20'
const plugin_name = "AT"

let enable_plugin = true;

const pageSize = 30;

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


async function searchMusic(query, page) {
    // console.log("searchMusic enable_plugin=", enable_plugin)
    if(!enable_plugin)
    {
        console.log("无效的Token, 本插件已禁用。")
        return;
    }

    let key_word = encodeURIComponent(query)
    let url_serch = host + "/so/" + key_word + ".html"
    // console.log(url_serch)
    let search_res = (await axios_1.default.get(url_serch)).data
    let song_list = await parse_play_list_html(search_res, " - ")

    const songs = song_list.map(formatMusicItem);

    return {
        isEnd: true,
        data: songs,
    };
}


async function getLyric(musicItem) {
    // console.log("getLyric:", musicItem)
    let res = (await (0, axios_1.default)({
        method: "get",
        url: host+"/plug/down.php?ac=music&lk=lrc&id=" + musicItem.id,
        timeout: 10000,
    })).data;
    res = res.replace("44h4", '****');  //屏蔽歌词中的网站信息
    res = res.replace("2t58", '****'); 
    res = res.replace("欢迎来访", '');  //屏蔽歌词中的网站信息
    res = res.replace("爱听音乐网", '');  //屏蔽歌词中的网站信息

    return {
        rawLrc: res
    };
}



async function getMediaSource(musicItem, quality) {
    // 咪咕音乐
    let migu_header = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": 'https://music.migu.cn/v3/music/player/audio',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.160 Safari/537.36',
        'Cookie':'mg_uem_user_id_9fbe6599400e43a4a58700a822fd57f8=37a10658-91ef-426e-968c-520d8339770f; cookieId=oSb_m5_8rUWM5nlCTqfK2eqNDnGDRPC1702187799997; migu_cookie_id=f61b1992-0de4-453d-ae3e-cf7142fb69e8-n41705568703420; idmpauth=true@passport.migu.cn; player_stop_open=0; playlist_adding=1; addplaylist_has=1; audioplayer_new=1; add_play_now=1; migu_music_status=true; migu_music_uid=91310317746; migu_music_avatar=; migu_music_nickname=%E5%92%AA%E5%92%95%E9%9F%B3%E4%B9%90%E7%94%A8%E6%88%B7; migu_music_level=0; migu_music_credit_level=1; migu_music_platinum=0; migu_music_msisdn=RgWeNzf7x3U2KyenRa1iYw%3D%3D; migu_music_email=; migu_music_sid=s%3A2zobVMI3vhlmNtoKMWwhoed7H_L5HTF7.kZjAo%2F3HJlyU5BHkPNVnvpYCq6oxqK7Z7GTAHfQojfw; playlist_change=0; audioplayer_exist=1; WT_FPC=id=210a55938b870e2962a1701846787994:lv=1705894245229:ss=1705894236704; audioplayer_open=1',
        'Accept':'application/json, text/plain, */*',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'zh-CN,zh;q=0.9',
        'Sec-Ch-Ua':'"Chromium";v="119", "Not?A_Brand";v="24"',
        'Sec-Ch-Ua-Mobile':'?0',
        'Sec-Ch-Ua-Platform':'"Windows"',
        'Sec-Fetch-Dest':'empty',
        'Sec-Fetch-Mode':'cors',
        'Sec-Fetch-Site':'same-origin',
        'copyrightId':'69905307287'
        // 'Host':'freetyst.nf.migu.cn',
        // '':'',
        // '':'',
        // '':'',
        // '':'',
    }
    // data 'U2FsdGVkX1/GXXembftBzkVg+XorJYtrkmDaadMyHacHQ4H5FQYDIntqtTKPm8hY/u0fIA0CoX12lqYyaYGiuTQVYpKrDkezIfVXyvgShNc='
    // seckey "FR4kJzWGL9AI0LvC5Q/NiEeyGIimkUXJjN/ZsWfNcPFabtgLkYV8/UOJmVfE5zSscrd/M0sGS7nmHTUEOOg0aduF2Vr8PHcmZfutgDtdfmxCiNF7NYrabEZGxF1jYV7EhUxvc9O45YMTHMaQpt/yjO/8GmB2uGBGH0N2rYejTWs="
    // raw "{\"copyrightId\":\"69905307287\",\"type\":1,\"auditionsFlag\":0}"
    let url1 =  'https://music.migu.cn/v3/api/music/audioPlayer/getPlayInfo?dataType=2&data=U2FsdGVkX1%2FGXXembftBzkVg%2BXorJYtrkmDaadMyHacHQ4H5FQYDIntqtTKPm8hY%2Fu0fIA0CoX12lqYyaYGiuTQVYpKrDkezIfVXyvgShNc%3D&secKey=FR4kJzWGL9AI0LvC5Q%2FNiEeyGIimkUXJjN%2FZsWfNcPFabtgLkYV8%2FUOJmVfE5zSscrd%2FM0sGS7nmHTUEOOg0aduF2Vr8PHcmZfutgDtdfmxCiNF7NYrabEZGxF1jYV7EhUxvc9O45YMTHMaQpt%2FyjO%2F8GmB2uGBGH0N2rYejTWs%3D'

    let migu_url = 'https://music.migu.cn/v3/api/music/audioPlayer/getPlayInfo'
    let migu_params = {
        'dataType': '2',
        'data':'U2FsdGVkX1%2B%2BGjN1Xi3AGtOr%2FjrulPwttii6%2BdsUVKBUVeEaTvOQ2ZsOeQJUcO1z04VSmNMXPfl9H45CwUT2l0oABs5dzZ9e6oy9KZrbt30%3D',
        'secKey':'X5vltlwuFsCmuZIANIE5DAw%2BL5z%2BjY4dq7Q%2B5Yh8PWCNqheinzc7bQoQxfNRoyUkwjzCJC5aDjVT2z2%2F%2FIGi%2BIAhS%2Fm81rCiiwD7Y79KiekhSo4%2Fo7ugWKUyNFU9BED1grll8cIY%2BBlimOb1oBENoBIYl1Mw7l%2FFa8nDfhsnaDs%3D',
    }

    // 酷我音乐

    let kuwo_header = {
        "Referer": 'http://www.kuwo.cn/play_detail/284892811',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.160 Safari/537.36',
        'Accept':'application/json, text/plain, */*',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'zh-CN,zh;q=0.9',
        'Cookie':'_ga=GA1.2.875517164.1701829707; uname3=Vale-%u53E4%u97EC; t3kwid=455674010; userid=455674010; websid=1751604101; pic3="http://img1.kuwo.cn/star/userhead/10/77/1661219150428_455674010.jpg"; t3=weixin; gid=95cfcb51-0be5-4436-b882-7ab582e7f0f0; Hm_lvt_cdb524f42f0ce19b169a8071123a4797=1704269407,1704768064,1704789754,1705900294; _gid=GA1.2.1036883917.1705900294; _gat=1; Hm_lpvt_cdb524f42f0ce19b169a8071123a4797=1705900312; _ga_ETPBRPM9ML=GS1.2.1705900295.14.1.1705900312.43.0.0; Hm_Iuvt_cdb524f42f0cer9b268e4v7y735ewrq2324=GH4GWymaRDi6877HfMPD6pacQBwd4pab',
        'Connection':'keep-alive',
        'host':'www.kuwo.cn',
        'Secret':'c49cc70312d5ba8cb4c835adeae81161b8e9cc96716dabd1914aa2699039020d01372592', //ok
        // '':'',
    }
    // data 'U2FsdGVkX1/GXXembftBzkVg+XorJYtrkmDaadMyHacHQ4H5FQYDIntqtTKPm8hY/u0fIA0CoX12lqYyaYGiuTQVYpKrDkezIfVXyvgShNc='
    // seckey "FR4kJzWGL9AI0LvC5Q/NiEeyGIimkUXJjN/ZsWfNcPFabtgLkYV8/UOJmVfE5zSscrd/M0sGS7nmHTUEOOg0aduF2Vr8PHcmZfutgDtdfmxCiNF7NYrabEZGxF1jYV7EhUxvc9O45YMTHMaQpt/yjO/8GmB2uGBGH0N2rYejTWs="
    // raw "{\"copyrightId\":\"69905307287\",\"type\":1,\"auditionsFlag\":0}"


    let kuwo_url = 'http://www.kuwo.cn/api/v1/www/music/playUrl'
    let kuwo_params = {
        'mid': '2316236',
        'type':'music',
        'httpsStatus':'1',
        // 'reqId': 'b6fc67b0-b8f4-11ee-8226-8fbca89f2aa6',//'65f5b190-b8eb-11ee-9783-81e5e04c2c72', '7a956320-b8eb-11ee-9783-81e5e04c2c72'ok 
        'plat': 'web_www',
        'from': '',
    }

    

    let mp3_Result = (await (0, axios_1.default)({
        method: "GET",
        url: kuwo_url,
        headers: kuwo_header,
        params: kuwo_params,
    })).data;

    // let res = (await axios_1.default.get(url1)).data;

    // console.log("search from third: ",mp3_Result)
    console.log(mp3_Result)

    // if(mp3_Result.url)
    // {
    //     return {
    //         url: mp3_Result.url,
    //         artwork: mp3_Result.pic,
    //     };
    // } 
    // return {
    //     url: ""
    // };
}


async function getMediaSource_86109(musicItem, quality) {
    // 86109音乐网

    let ws_header = {
        "Referer": 'http://www.86109.com/down.php?ac=music&id=69905307215&lk=320',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.160 Safari/537.36',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.9',
        'Cookie':'Hm_lvt_ccb84034ce6005ec3c4528e631e0ad8e=1705294833,1705364128,1705537228,1705911797; Hm_lpvt_ccb84034ce6005ec3c4528e631e0ad8e=1705911873',
        'Connection':'keep-alive',
        'host':'api.86109.com',
    }


    let ws_url = 'http://api.86109.com/mgmp3/69905307215.mp3'
    let ws_params = {
        'ac': 'music',
        'id':'69905307215',
        'lk':'320',
    }

    let ws_url1 = 'http://www.86109.com/down.php?ac=music&id=69905307215&lk=320'

    let mp3_Result = (await (0, axios_1.default)({
        method: "GET",
        url: ws_url,
        headers: ws_header,
        // data: ws_params,
    })).data;

    let res = (await axios_1.default.get(ws_url1)).data;

    // console.log("search from third: ",mp3_Result)
    console.log(mp3_Result)

    // if(mp3_Result.url)
    // {
    //     return {
    //         url: mp3_Result.url,
    //         artwork: mp3_Result.pic,
    //     };
    // } 
    // return {
    //     url: ""
    // };
}
// getMediaSource_86109()


async function getMediaSource_90t8(musicItem, quality) {
    // 90t8音乐网

    let ws_header = {
        "Referer": 'http://www.90t8.com/mp3/a39ad183a8a32e7d97b0320ff210ee32.html',
        // 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.160 Safari/537.36',
        // 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        // 'Accept-Encoding':'gzip, deflate',
        // 'Accept-Language':'zh-CN,zh;q=0.9',
        'Cookie':'Hm_lvt_a33f51a72fc140eb7044c0d7a431d116=1704434875,1704624111,1704684835,1705882727; mode=1; songIndex=0; down_mima=ok; coin_screen=1536*864; Hm_lpvt_a33f51a72fc140eb7044c0d7a431d116=1705913024',
        // 'Connection':'keep-alive',
        'host':'www.90t8.com',
    }


    let ws_url = 'http://www.90t8.com/plug/down.php'
    let ws_params = {
        'ac': 'music',
        'id':'a39ad183a8a32e7d97b0320ff210ee32',
        // 'lk':'320',
    }

    let ws_url1 = 'http://www.90t8.com/plug/down.php?ac=music&id=a39ad183a8a32e7d97b0320ff210ee32'

    let mp3_Result = (await (0, axios_1.default)({
        method: "GET",
        url: ws_url,
        headers: ws_header,
        params: ws_params,
        responseType:'stream',
    })).data;


    // let res = (await axios_1.default.get(ws_url1, ws_header, 'stream')).data;

    // console.log("search from third: ",mp3_Result)
    console.log(mp3_Result.responseUrl)
    // console.log(res)

    // if(mp3_Result.url)
    // {
    //     return {
    //         url: mp3_Result.url,
    //         artwork: mp3_Result.pic,
    //     };
    // } 
    // return {
    //     url: ""
    // };
}
// getMediaSource_90t8()

async function getMediaSource_90t8_1(musicItem, quality) {
    // 90t8音乐网

    let ws_header = {
        "Referer": 'http://www.90t8.com/mp3/efebdc94f35d5aa6ddeefccebe253e00.html',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; Moto G (4)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Mobile Safari/537.36 Edg/89.0.774.68',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.9',
        // 'Cookie':'down_mima=ok; Hm_lvt_a33f51a72fc140eb7044c0d7a431d116=1705882727,1705973522,1706516952,1706586970; Hm_lpvt_a33f51a72fc140eb7044c0d7a431d116=1706586978',
        'Cookie':'down_mima=ok',

        'Connection':'keep-alive',
        "Content-Type": "application/x-www-form-urlencoded",
        'host':'www.90t8.com',
    }


    let ws_url = 'http://www.90t8.com/plug/down.php'
    let ws_params = {
        'ac': 'music',
        'id':'efebdc94f35d5aa6ddeefccebe253e00',
        // 'lk':'320',
    }

    let mp3_Result = await axios_1({
        method: "GET",
        url: ws_url,
        headers: ws_header,
        params: ws_params,
        // responseType:'stream',
        withCredentials: true,
    });
    console.log("search from third: ",mp3_Result.request.host)
    console.log("search from third: ",mp3_Result.request.path)
    console.log("https://"+mp3_Result.request.host+mp3_Result.request.path)
    // let res = (await axios_1.default.get(ws_url1, ws_header, 'stream')).data;

    // console.log("search from third: ",mp3_Result)
    // console.log(mp3_Result.responseUrl)
    // console.log(res)

    // if(mp3_Result.url)
    // {
    //     return {
    //         url: mp3_Result.url,
    //         artwork: mp3_Result.pic,
    //     };
    // } 
    // return {
    //     url: ""
    // };
}
// getMediaSource_90t8_1()

async function getMediaSource_90t8_2() {
    // 90t8音乐网

    let ws_header = {
        // "Referer": 'http://www.90t8.com/mp3/a39ad183a8a32e7d97b0320ff210ee32.html',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.160 Safari/537.36',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.9',
        'Cookie':'Hm_lvt_a33f51a72fc140eb7044c0d7a431d116=1704434875,1704624111,1704684835,1705882727; mode=1; songIndex=0; down_mima=ok; coin_screen=1536*864; Hm_lpvt_a33f51a72fc140eb7044c0d7a431d116=1705913024',
        'Connection':'keep-alive',
        'host':'www.90t8.com',
    }


    let ws_url = 'http://www.90t8.com/plug/down.php'
    let ws_params = {
        'ac': 'music',
        'id':'a39ad183a8a32e7d97b0320ff210ee32',

        // 'lk':'320',
    }




    let ws_url1 = 'http://www.90t8.com/plug/down.php?ac=music&id=a39ad183a8a32e7d97b0320ff210ee32'

    const options = {
        url: ws_url1,       //请求链接
        // hostname: 'http://www.90t8.com', // 请求的主机名
        // path: '/plug/down.php', // 请求的路径
        // port: 80, // 请求的端口号
        method: 'GET',  //请求方式
        headers: ws_header,   //设置请求头
        // params: ws_params,
        // responseType:'stream',
    }

    let mp3_url = ""
    let raw_Headers = []
    const req = http.request(options.url, options, res => {
        let buf = ''
        res.on('data', d => buf += d) //获得Stream流，需要合并

        res.on('end', () => console.log(buf)) //数据接收完毕
        console.log(buf)
        // console.log(res)
        raw_Headers = res.rawHeaders
        console.log(raw_Headers[3])
        
    })
    
    req.on('error', error => console.error(error)) //显示错误信息
    req.end()
    // return res
    
}
// getMediaSource_90t8_2()

async function getMediaSource_90t8_3(musicItem, quality) {
    // 90t8音乐网

    let ws_header = {
        "Referer": 'http://www.90t8.com/mp3/a39ad183a8a32e7d97b0320ff210ee32.html',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; Moto G (4)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Mobile Safari/537.36 Edg/89.0.774.68',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.9',
        // 'Cookie':'down_mima=ok; Hm_lvt_a33f51a72fc140eb7044c0d7a431d116=1705882727,1705973522,1706516952,1706586970; Hm_lpvt_a33f51a72fc140eb7044c0d7a431d116=1706586978',
        'Cookie':'down_mima=ok',

        'Connection':'keep-alive',
        "Content-Type": "application/x-www-form-urlencoded",
        'host':'www.90t8.com',
    }


    let ws_url = 'http://www.90t8.com/plug/down.php'
    let ws_params = {
        'ac': 'music',
        'id':'a39ad183a8a32e7d97b0320ff210ee32',
        // 'lk':'320',
    }

    let ws_url1 = 'http://www.90t8.com/plug/down.php?ac=music&id=a39ad183a8a32e7d97b0320ff210ee32'


    let mp3_Result = await fetch(ws_url1, {
        method: 'get',
        headers: ws_header,
    });
    console.log("search from third: ",mp3_Result.url)

    // let res = (await axios_1.default.get(ws_url1, ws_header, 'stream')).data;

    // console.log("search from third: ",mp3_Result)
    // console.log(mp3_Result.responseUrl)
    // console.log(res)

    // if(mp3_Result.url)
    // {
    //     return {
    //         url: mp3_Result.url,
    //         artwork: mp3_Result.pic,
    //     };
    // } 
    // return {
    //     url: ""
    // };
}
getMediaSource_90t8_3()


async function getMediaSource_dda5(musicItem, quality) {
    // dda5音乐网

    let dd_header = {
        "Referer": 'http://www.dda5.com/down/60054702010.html',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.160 Safari/537.36',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.9',
        'Cookie':'Hm_lvt_e95826125a9b79c89c364177c5446a7c=1705537321,1705651053,1705911789,1705969512; mode=1; songIndex=0; coin_screen=1536*864; down_mima=ok; Hm_lpvt_e95826125a9b79c89c364177c5446a7c=1705972939',
        // 'Cookie':'Hm_lvt_a33f51a72fc140eb7044c0d7a431d116=1704434875,1704624111,1704684835,1705882727; mode=1; songIndex=0; down_mima=ok; coin_screen=1536*864; Hm_lpvt_a33f51a72fc140eb7044c0d7a431d116=1705913024',
        'Connection':'keep-alive',
        'host':'www.dda5.com',
        'Content-type':'application/x-www-form-urlencoded; charset=UTF-8',
        'Upgrade-Insecure-Requests':'1',

    }


    let dd_url = 'http://www.dda5.com/plug/down.php'
    let dd_params = {
        'ac': 'music',
        'id':'60054702010',
        'lk':'320',
    }

    // let ws_url1 = 'http://www.90t8.com/plug/down.php?ac=music&id=106ec000715c5c62aae36b347b296642'

    let mp3_Result = (await (0, axios_1.default)({
        method: "GET",
        url: dd_url,
        headers: dd_header,
        params: dd_params,
        responseType:'stream',
    })).data;


    // let res = (await axios_1.default.get(ws_url1, ws_header)).data;

    // console.log("search from third: ",mp3_Result)
    console.log(encodeURIComponent(mp3_Result.responseUrl))
    console.log(encodeURI(mp3_Result.responseUrl))
    console.log(mp3_Result.responseUrl)

    // if(mp3_Result.url)
    // {
    //     return {
    //         url: mp3_Result.url,
    //         artwork: mp3_Result.pic,
    //     };
    // } 
    // return {
    //     url: ""
    // };
}
// getMediaSource_dda5()


async function getMediaSource_guoheyinyue(musicItem, quality) {
    // // music.ghxi.com/

    let _header = {
        "Referer": 'https://music.ghxi.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.160 Safari/537.36',
        'Accept':'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'zh-CN,zh;q=0.9',
        'Cookie':'Hm_lvt_66e607dca971ebaef3c48ae46872065c=1706750924; PHPSESSID=mqubbi4prnrurq8aecngbb2pp4',
        'Content-type':'application/x-www-form-urlencoded; charset=UTF-8',

        'Origin':'https://music.ghxi.com',
        'X-Requested-With':'XMLHttpRequest',
        'Sec-Fetch-Site':'same-origin',
        'Sec-Fetch-Dest':'empty',
        'Sec-Fetch-Mode':'cors',
        'Sec-Ch-Ua':'"Chromium";v="119", "Not?A_Brand";v="24"',
        'Sec-Ch-Ua-Mobile':'?0',
        'Sec-Ch-Ua-Platform':'"Windows"',
    }


    let _url = 'https://music.ghxi.com/wp-admin/admin-ajax.php'
    let _params = {
        action: 'gh_music_ajax',
        type: 'getMusicUrl',
        // type: 'search',
        music_type: 'qq',
        music_size: '128',
        songid: '1f10D1wDeGvfYEgvqHDNe9rrpWpW1KvJCO9R26GSxqVHyPBCcmeLzlwXAg',
    }

    let _url1 = 'https://music.ghxi.com/wp-admin/admin-ajax.php?action=gh_music_ajax&type=getMusicUrl&music_type=qq&music_size=128&songid=1f10D1wDeGvfYEgvqHDNe9rrpWpW1KvJCO9R26GSxqVHyPBCcmeLzlwXAg'



    // let  aaa = qs.stringify(_url)
    // console.log(aaa)
    var params = new URLSearchParams();
    params.append('action', 'gh_music_ajax')
    params.append('type', 'getMusicUrl')
    params.append('music_type', 'qq')
    params.append('music_size', '128')
    params.append('songid', '1f10D1wDeGvfYEgvqHDNe9rrpWpW1KvJCO9R26GSxqVHyPBCcmeLzlwXAg')

    // let mp3_Result = await axios_1({
    //     method: "post",
    //     url: _url,
    //     headers: _header,
    //     data: params,
    //     // responseType:'json',
    //     withCredentials: true,
    // });

    // let mp3_Result = (await (0, axios_1.default)({
    //     method: "POST",
    //     url: _url1,
    //     headers: _header,
    //     // params: _params,
    //     responseType:'json',
    //     withCredentials: true,
    // }));


    // let mp3_Result = await axios_1.post(_url, _params,
    //     {
    //         headers: _header,
    //         // params: _params,
    //         // responseType:'json',
    //         withCredentials: true,
    //     }
    // );

    let mp3_Result = await fetch(_url,{
    	headers: _header,
        method:"POST",
        body:"action=gh_music_ajax&type=getMusicUrl&music_type=qq&music_size=128&songid=1f10D1wDeGvfYEgvqHDNe9rrpWpW1KvJCO9R26GSxqVHyPBCcmeLzlwXAg"
    })
                        



    // let res = (await axios_1.default.get(ws_url1, ws_header)).data;

    console.log("search from third: ",mp3_Result)

}
// getMediaSource_guoheyinyue()




async function getMediaSource_yinyueke(musicItem, quality) {
    

    let _header = {
        "Referer": 'https://www.yinyueke.net/player/index.html',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.160 Safari/537.36',
        'Accept':'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'zh-CN,zh;q=0.9',
        // 'Cookie':'Hm_lvt_e95826125a9b79c89c364177c5446a7c=1705537321,1705651053,1705911789,1705969512; mode=1; songIndex=0; coin_screen=1536*864; down_mima=ok; Hm_lpvt_e95826125a9b79c89c364177c5446a7c=1705972939',
        'Connection':'keep-alive',
        'Sec-Ch-Ua':'"Chromium";v="119", "Not?A_Brand";v="24"',
        'Sec-Ch-Ua-Mobile':'?0',
        'Content-type':'application/x-www-form-urlencoded; charset=UTF-8',
        'Upgrade-Insecure-Requests':'1',
    }


    let _url = 'https://player.yinyueke.net/api/index.php?server=netease&type=url&id=2124381474'
    let _params = {
        server: 'qq',
        type: 'url',
        id: '2057534370',
    }

    let _url1 = 'https://player.yinyueke.net/api/index.php'

    let mp3_Result = await fetch(_url, {
        method: "GET",
        
        headers: _header,
        // data: _params,
    })//.data;

    // let mp3_Result = await axios_1({
    //     method: "post",
    //     url: _url,
    //     headers: _header,
    //     // params: _params,
    //     responseType:'stream',
    //     withCredentials: true,
    // });



    // let res = (await axios_1.default.get(ws_url1, ws_header)).data;

    console.log("search from third: ",mp3_Result.url)

}
// getMediaSource_yinyueke()



async function getMediaSource_33z3(musicItem, quality) {
    
    let _header = {
        "Referer": 'http://www.33z3.com/play/ZWZrZWprZmVoag.html',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; Moto G (4)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Mobile Safari/537.36 Edg/89.0.774.68',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.9',
        // 'Cookie':'down_mima=ok; Hm_lvt_a33f51a72fc140eb7044c0d7a431d116=1705882727,1705973522,1706516952,1706586970; Hm_lpvt_a33f51a72fc140eb7044c0d7a431d116=1706586978',
        'Cookie':'down_mima=ok',

        'Connection':'keep-alive',
        "Content-Type": "application/x-www-form-urlencoded",
        'host':'http://www.33z3.com',
    }


    let _url1 = 'http://www.33z3.com/plug/down.php?ac=dmp3&id=ZWZrZWprZmVoag&type=320'


    let mp3_Result = await fetch(_url1, {
        method: 'get',
        headers: _header,
    });
    console.log("search from third: ",mp3_Result.url)

}
// getMediaSource_33z3()

async function getMediaSource_gdStudio(musicItem, quality) {
    
    let _header = {
        "Referer": 'https://music.gdstudio.xyz/',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; Moto G (4)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Mobile Safari/537.36 Edg/89.0.774.68',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.9',
        // 'Cookie':'down_mima=ok; Hm_lvt_a33f51a72fc140eb7044c0d7a431d116=1705882727,1705973522,1706516952,1706586970; Hm_lpvt_a33f51a72fc140eb7044c0d7a431d116=1706586978',
        // 'Cookie':'down_mima=ok',

        'Connection':'keep-alive',
        "Content-Type": "application/x-www-form-urlencoded",
        'Origin':'https://music.gdstudio.xyz',
    }


    // let _url = 'https://music.gdstudio.xyz/api.php?callback=jQuery111303825341212578255_1707741115691'
    let _url = 'https://music.gdstudio.xyz/api.php?'

    let _params = {
        br: '320',
        types: 'url',
        source: 'netease',
        id: '2124381474',
    }


    let mp3_Result = await axios_1({
        method: "post",
        url: _url,
        headers: _header,
        params: _params,
        // responseType:'stream',
        // withCredentials: true,
    });

    // let mp3_Result = await fetch(_url,{
    // 	headers: _header,
    //     method:"POST",
    //     data: _params,
    // })

    console.log("search from third: ",mp3_Result.data)

}
// getMediaSource_gdStudio()


async function getMediaSource_m326(musicItem, quality) {
    // 90t8音乐网

    let ws_header = {
        "Referer": 'http://www.m326.com/sing/481d3f144fc7a6a2ab739de756988e85.html',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.160 Safari/537.36',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.9',
        'Cookie':'Hm_lvt_4542ba18f05631bdfefe8b5ccf401e8c=1705364212,1705911307,1706519090,1706592319; Hm_lpvt_4542ba18f05631bdfefe8b5ccf401e8c=1706592605',
        'Connection':'keep-alive',
        'host':'www.m326.com',
    }


    let ws_url = 'http://www.m326.com/data/down.php'
    let ws_params = {
        'ac': 'music',
        'id':'481d3f144fc7a6a2ab739de756988e85',
        // 'lk':'320',
    }

    let ws_url1 = 'http://www.90t8.com/data/down.php?ac=music&id=481d3f144fc7a6a2ab739de756988e85'

    let mp3_Result = (await (0, axios_1.default)({
        method: "POST",
        url: ws_url1,
        headers: ws_header,
        // params: ws_params,
        responseType:'stream',

    })).data;


    // let res = (await axios_1.default.get(ws_url1, ws_header, 'stream')).data;

    // console.log("search from third: ",mp3_Result)
    console.log(mp3_Result.responseUrl)
    // console.log(res)

    // if(mp3_Result.url)
    // {
    //     return {
    //         url: mp3_Result.url,
    //         artwork: mp3_Result.pic,
    //     };
    // } 
    // return {
    //     url: ""
    // };
}
// getMediaSource_m326()

async function getMediaSource_56yinyuewang(musicItem, quality) {
    // 56音乐网

    // let _header = {
    //     "Referer": 'https://www.wltj56.cn/mp3/325386987',
    //     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.160 Safari/537.36',
    //     'Accept':'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
    //     'Accept-Encoding':'gzip, deflate, br',
    //     'Accept-Language':'zh-CN,zh;q=0.9',
    //     'Cookie':'cscms_session=umg2uot7fsduu3hl8777uo6ah43qd2fk',
    //     'Content-type':'application/x-www-form-urlencoded; charset=UTF-8',

    //     'Origin':'https://www.wltj56.cn',
    //     'X-Requested-With':'XMLHttpRequest',
    //     'Sec-Fetch-Site':'same-origin',
    //     'Sec-Fetch-Dest':'empty',
    //     'Sec-Fetch-Mode':'cors',
    //     'Sec-Ch-Ua':'"Chromium";v="119", "Not?A_Brand";v="24"',
    //     'Sec-Ch-Ua-Mobile':'?0',
    //     'Sec-Ch-Ua-Platform':'"Windows"',
    // }
    // let _url = 'https://www.wltj56.cn/index.php/so/add'

    // let mp3_Result  = await axios_1.default.get(_url, _header);

    // let _params= {
    //     "id": '325386987',
    //     "name": "圣诞星 (feat. 杨瑞代)",
    //     "sid": '336',
    //     "sname": "周杰伦",
    //     "pic": "https://img3.kuwo.cn/star/albumcover/500/s3s60/29/1448169300.jpg",
    //     "aid": '45277297',
    //     "aname": "圣诞星&nbsp;(feat.&nbsp;杨瑞代)",
    //     "mv": "1",
    //     'singerid':'66',
    // }

    // let mp3_Result = await axios_1.post(_url, _params,
    //     {
    //         headers: _header,
    //         // responseType:'json',
    //         withCredentials: true,
    //     }
    // )   // 最终的响应：data: {code: 200,lkid: '399645',url: 'https://www.wltj56.cn/music/399645'}

    let _url = 'https://www.wltj56.cn/lkdata/getkw/325386987.mp3'
    let _header = {
        "Referer": 'https://www.wltj56.cn/mp3/325386987',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.160 Safari/537.36',
        'Accept':'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
        'Accept-Encoding':'identity;q=1, *;q=0',
        'Accept-Language':'zh-CN,zh;q=0.9',
        'Cookie':'cscms_session=umg2uot7fsduu3hl8777uo6ah43qd2fk',
        'Range':'bytes=0-',

        'Origin':'https://www.wltj56.cn',
        'Sec-Fetch-Site':'same-origin',
        'Sec-Fetch-Dest':'audio',
        'Sec-Fetch-Mode':'no-cors',
        'Sec-Ch-Ua':'"Chromium";v="119", "Not?A_Brand";v="24"',
        'Sec-Ch-Ua-Mobile':'?0',
        'Sec-Ch-Ua-Platform':'"Windows"',
    }


    // let mp3_Result = await axios_1({
    //     method: "GET",
    //     url: _url,
    //     headers: _header,
    //     // params: _params,
    //     responseType:'stream',
    //     withCredentials: true,
    // });
    // console.log("search from third: ",mp3_Result)

    let mp3_Result = await fetch(_url,{
    	headers: _header,
        method:"get",
    })



    console.log(mp3_Result.url)
    // console.log(res)

    // if(mp3_Result.url)
    // {
    //     return {
    //         url: mp3_Result.url,
    //         artwork: mp3_Result.pic,
    //     };
    // } 
    // return {
    //     url: ""
    // };
}
// getMediaSource_56yinyuewang()

async function getMediaSource_lx(musicItem, quality) {
    // 落雪音乐接口

    // let _url = 'http://110.41.172.118:9763/url/wy/5283519/320k'   //ikun
    // let _url = 'http://103.40.13.21:9763/url/kw/281472652/320k'        //nya
    // let _url = 'http://127.0.0.1:9763/url/kw/281472652/128k'        //local
    // let _url = 'https://6api.itooi.cn/url/tx/004coY9R3he5Oh/128k'        //liuyin
    let _url = 'https://share.duanx.cn/url/wy/5283519/320k'        //

    let mp3_Result = await axios_1({
        method: "GET",
        url: _url,
        // headers: _header,
        // params: _params,
        // responseType:'stream',
        // withCredentials: true,
    });
    // console.log("search from third: ",mp3_Result)

    let res = mp3_Result.data
    console.log(res)
    // console.log(res)

}
// getMediaSource_lx()

async function getMediaSource_kg_gainianban(musicItem, quality) {
    // 落雪音乐接口

    let _url = 'https://tracker.kugou.com/i/v2/?album_id=75998334&userid=0&area_code=1&hash=55a32087ee33df26c928c7bf4d4a61bf&module=&appid=3166&version=23606&vipType=65530&ptype=0&token=&page_id=748374614&mtype=0&album_audio_id=533712476&behavior=play&pid=421&cmd=26&ppage_id=463467626,274763458,367482925&IsFreePart=1&mid=257996537816922589531455904235228039332&dfid=3MIaLo4KniSQ2feqGO0HJt1M&pidversion=3001&key=e4a466ff599b4c8281d3a0b87251e7f0&with_res_tag=1'

    let mp3_Result = await axios_1({
        method: "GET",
        url: _url,
        // headers: _header,
        // params: _params,
        // responseType:'stream',
        // withCredentials: true,
    });
    // console.log("search from third: ",mp3_Result)

    let res = mp3_Result
    console.log(res)
    // console.log(res)

}
// getMediaSource_kg_gainianban()

async function getMediaSource_gwqubao(musicItem, quality) {
    // 落雪音乐接口

    let _url = 'https://www.gequbao.com/api/play_url?id=402856&json=1'

    let mp3_Result = await axios_1({
        method: "GET",
        url: _url,
    });
    // console.log("search from third: ",mp3_Result)

    let res = mp3_Result.data.data.url
    console.log(res)
    // console.log(res)

}
// getMediaSource_gwqubao()


async function getMediaSource_ilingku(musicItem, quality) {

    let _url = 'http://wapi.ilingku.com/wechat/boxapi/mp3.php?rid=f261350d64Y3bkX1wKXwMPF1EHBw4EAQAGDwA'

    let _header = {
        "Host": 'wapi.ilingku.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.160 Safari/537.36',
        'Accept':'*/*',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.9',
        'Connection': 'Keep-Alive',
        'Origin': 'http://box.flac.ltd',
        'Referer': 'http://box.flac.ltd/'
    }

    let mp3_Result = await axios_1({
        method: "GET",
        url: _url,
        headers: _header,
        // params: _params,
        // responseType:'stream',
        withCredentials: true,
    });

    // let mp3_Result = await fetch(_url,{
    // 	headers: _header,
    //     method:"get",
    // })
    // console.log("search from third: ",mp3_Result)

    let res = mp3_Result
    console.log(res)
    // console.log(res)

}
// getMediaSource_ilingku()


// searchMusic("告白气球").then(console.log)
// getLyric()
// getTopLists().then(console.log)
// getRecommendSheetTags().then(console.log)

// let music_item = {
//     id: 'bnd4c3ZoZA',
//     songmid: undefined,
//     title: '告白气球',
//     artist: '周杰伦',
//     artwork: undefined,
//     album: undefined,
//     lrc: undefined,
//     albumid: undefined,
//     albummid: undefined
//   }
// getMediaSource(music_item)

// let top_item={
//     id: "/list/top.html",
//     coverImg: undefined,
//     title: "酷我飙升榜",
//     description: "酷我每日搜索热度飙升最快的歌曲排行榜，按搜索播放数据对比前一天涨幅排序，每天更新",
// }

// getTopListDetail(top_item)

// let tag = {
//     id: '/singerlist/huayu/index/index/index.html', 
//     title: '华语歌手', 
//     digest: "singer" ,
//     sign: "song"
// }

// let tag1 = {
//     id: '/playtype/douyin.html', 
//     title: '抖音', 
//     digest: "song" 
// }

// let tag2 = {
//     title: '默认', 
//     // digest: "singer" 
// }
// getRecommendSheetsByTag(tag).then(console.log)


// let singer = 
// {
//     title: '周杰伦',
//     artist: undefined,
//     id: '/singer/ZGRj.html',
//     artwork: 'http://tu.eev3.com/t.php?h=100&w=100&url=http://img1.kuwo.cn/star/starheads/300/8/10/2150960774.jpg',
//     playCount: undefined,
//     createUserId: undefined,
//     sign: 'singer'
// }


// getMusicSheetInfo(singer, 0).then(console.log)
  /// 接口
  // 音乐热歌榜接口地址  :  https://music.163.com/api/playlist/detail?id=3778678static const String musicApiUrl_host = "music.163.com";static const String musicApiUrl_path = "/api/playlist/detail";
  // 音乐搜索  http://musicapi.leanapp.cn/search?keywords=static const String musicSearchUrl_host = "musicapi.leanapp.cn";static const String musicSearchUrl_path = "/search";
  // 音乐评论  http://musicapi.leanapp.cn/comment/music?id=27588968&limit=1static const String musicCommentUrl_host = "musicapi.leanapp.cn";static const String musicCommentUrl_path = "/comment/music";
  // 音乐播放地址 https://api.imjad.cn/cloudmusic/?type=song&id=112878&br=128000
  // 音乐歌词    https://api.imjad.cn/cloudmusic/?type=lyric&id=112878&br=128000static const String musicPlayLyricUrl_host = "api.imjad.cn";static const String musicPlayLyricUrl_path = "/cloudmusic";// 个人歌单// http://music.163.com/api/user/playlist/?offset=0&limit=100&uid=1927677638static const String personalPlayListApiUrl_host = "music.163.com";static const String personalPlayListApiUrl_path = "/api/user/playlist";
  // 个人信息// https://music.163.com/api/v1/user/detail/1927677638static const String personalInfoUrl_host = "music.163.com";static const String personalInfoUrl_path = "/api/v1/user/detail/";// 歌单详情 https://music.163.com/api/playlist/detail?id=24381616static const String playlistDetailUrl_host = "music.163.com";static const String playlistDetailUrl_path = "/api/playlist/detail";// 歌单评论 http://musicapi.leanapp.cn/comment/playlist?id=1static const String playlistCommentUrl_host = "musicapi.leanapp.cn";static const String playlistCommentUrl_path = "/comment/playlist";
  // 精品歌单 http://musicapi.leanapp.cn/top/playlist/highquality/华语static const String playlistHighQualityUrl_host = "musicapi.leanapp.cn";static const String playlistHighQualityUrl_path = "/top/playlist/highquality";
  // 相似歌单  http://musicapi.leanapp.cn/simi/playlist?id=347230static const String playlistSimiUrl_host = "musicapi.leanapp.cn";static const String playlistSimiUrl_path = "/simi/playlist";// 歌手榜单  http://music.163.com/api/artist/list   http://musicapi.leanapp.cn/artist/liststatic const String singerRankUrl_host = "musicapi.leanapp.cn";static const String singerRankUrl_path = "/artist/list";// 歌手热门歌曲 http://music.163.com/api/artist/5781  歌手信息和热门歌曲static const String singerTopMusicUrl_host = "music.163.com";static const String singerTopMusicUrl_path = "/api/artist/";// 歌手专辑列表 http://music.163.com/api/artist/albums/3684  歌手id  http://musicapi.leanapp.cn/artist/album?id=6452&limit=30static const String singerAlbumUrl_host = "music.163.com";static const String singerAlbumUrl_path = "/api/artist/albums/";// 专辑详情  https://music.163.com/api/album/90743831   专辑idstatic const String albumDetailUrl_host = "music.163.com";static const String albumDetailUrl_path = "/api/album/";
  // 歌手描述 http://musicapi.leanapp.cn/artist/desc?id=6452static const String singerDescUrl_host = "musicapi.leanapp.cn";static const String singerDescUrl_path = "/artist/desc";// 歌曲MV  http://music.163.com/api/mv/detail?id=319104&type=mp4
