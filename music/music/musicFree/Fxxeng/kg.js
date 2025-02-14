"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const axios_1 = require("axios");
const he = require("he");
const cheerio_1 = require("cheerio");
const CryptoJS = require("crypto-js");

const host = "http://ww" + "w.90" + "t8.com"
const token_host = "https://a" + "gi" + "t.ai"
const token_txt = 'token_date: 2023-12-20'

let enable_plugin = true;
const plugin_name = "酷狗"

const pageSize = 30;
let music_info = {
    url: "",
    rawLrc: "",
    artwork: "",
}


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

async function parse_play_list_html(raw_data, separator) {
    const $ = cheerio_1.load(raw_data);
    const raw_play_list = $("div.main").find("li");
    let song_list_arr = [];
    for(let i=0; i<raw_play_list.length; i++)
    {
        const item=$(raw_play_list[i]).find("a");
        
        let data_id = $(item[0]).attr("href").match(/\/mp3\/(.*?).html/)[1]
        // console.log($(item[0]).text())
        let _text = $(item[0]).text()
        let separated_text =_text.split(separator)
        let data_artist = separated_text[0] // 通过分隔符区分歌手和歌名
        let data_title = separated_text[1]!="" ? separated_text[1]:separated_text[2];
        data_title = (data_title.split("》"))[0];
        song_list_arr.push({
            id: data_id, 
            title: data_title, 
            artist: data_artist,
        })
    }
    // console.log("song_list_arr:",song_list_arr)
    return(song_list_arr)
}

async function parse_top_list_html(raw_data) {
    const $ = cheerio_1.load(raw_data);
    const raw_play_list = $("div.gt").find("li");
    const page_data = $($($("div.main")[0]).find("div")[1]).text();
    let cover_img = "https://agit.ai/vale_gtt/MSC_API/raw/branch/master/my_plugins/third_party/logo/kg.jpg"
    let hot_list = [];
    for(let i=1; i<12; i++)
    {
        const item=$(raw_play_list[i]).find("a");
        let data_address = $(item[0]).attr("href")
        let data_title = $(item[0]).text()
        data_title = data_title.replace('TOP排行榜','酷狗TOP500')
        hot_list.push({
            id: data_address, 
            coverImg: cover_img,
            title: data_title, 
            description: "每日同步官方数据。" + page_data
        })
    }
    let spectial_list = []
    for(let i=13; i<24; i++)
    {
        const item=$(raw_play_list[i]).find("a");
        let data_address = $(item[0]).attr("href")
        let data_title = $(item[0]).text()
        spectial_list.push({
            id: data_address, 
            coverImg: cover_img,
            title: data_title, 
            description: "每日同步官方数据。" + page_data
        })
    }
    let global_list = []
    for(let i=26; i<36; i++)
    {
        const item=$(raw_play_list[i]).find("a");
        let data_address = $(item[0]).attr("href")
        let data_title = $(item[0]).text()
        global_list.push({
            id: data_address, 
            coverImg: cover_img,
            title: data_title, 
            description: "每日同步官方数据。" + page_data
        })
    }
    // console.log("song_list_arr:",song_list_arr)
    return {
        hot_list,
        spectial_list,
        global_list
    };
    
}

async function parse_play_type_html(raw_data) {
    // 解析歌单分类
    const $ = cheerio_1.load(raw_data);
    const raw_group_list = $("div.gt").find("li")
    let group_list =[]
    let play_type =[]
    for(let i=1; i<raw_group_list.length; i++)
    {
        let data_address = $(raw_group_list[i]).find("a").attr("href")
        let data_title = $(raw_group_list[i]).text()
        play_type.push({
            id: data_address,
            digest: "song",
            title: data_title,
            sign: "song"
        })


    }
    group_list.push({
        name:'歌单分类',
        data: play_type,
    })
    return group_list;
}

async function parse_singer_type_html(raw_data) {
    // 解析歌手分类
    const $ = cheerio_1.load(raw_data);
    // console.log(raw_data)
    const raw_group_list = $("div.gt").find("li")
    let group_list =[]
    let play_type =[]
    for(let i=1; i<raw_group_list.length; i++)
    {
        let data_address = $(raw_group_list[i]).find("a").attr("href")
        let data_title = $(raw_group_list[i]).text()
        play_type.push({
            id: data_address,
            digest: "singer",
            title: data_title,
            sign: "singer"
        })


    }
    // console.log(play_type)
    group_list.push({
        name:'歌手分类',
        data: play_type,
    })
    return group_list;
}

async function parse_song_list_html(raw_data) {
    // 解析歌单分类中的歌单列表
    const $ = cheerio_1.load(raw_data);
    const raw_song_list = $("div.mv_list").find("li")
    // $(raw_group_list[i]).find("li")
    let song_list = []
    for(let i=0; i<raw_song_list.length; i++)
    {
        let item_1 = $(raw_song_list[i]).find("a")
        let data_id = $(item_1[0]).attr("href")
        let data_title = $(raw_song_list[i]).find("img").attr("title")
        let data_img = $(raw_song_list[i]).find("img").attr("src")
        song_list.push({
            name: data_title,
            uname: undefined,
            id: data_id,
            img: data_img,
            listencnt: undefined,
            uid: undefined,
            sign: "song"
        })
    }
    let total  = $("div.pagedata").find("span").text();
    return {
        count: total,
        list: song_list,
    };
}

async function parse_singer_list_html(raw_data) {
    // 解析歌单分类中的歌单列表
    const $ = cheerio_1.load(raw_data);
    const raw_song_list = $("div.gs_list").find("li")
    // $(raw_group_list[i]).find("li")
    let song_list = []
    for(let i=0; i<raw_song_list.length; i++)
    {
        let item_1 = $(raw_song_list[i]).find("a")
        let data_id = $(item_1[0]).attr("href")
        let data_title = $(raw_song_list[i]).find("img").attr("title")
        let data_img = $(raw_song_list[i]).find("img").attr("src")
        song_list.push({
            name: data_title,
            uname: undefined,
            id: data_id,
            img: data_img,
            listencnt: undefined,
            uid: undefined,
            sign: "singer"
        })
    }
    let total  = $("div.pagedata").find("span").text();
    return {
        count: total,
        list: song_list,
    };
}

// 获取歌单，包括歌单+歌手分类
async function get_play_Sheet_Tags() {
    // 获取歌单页面内容
    //let play_type_url = host + "/gdlist/hot/1.html"
    // console.log(url_serch)
    //let play_type_html = (await axios_1.default.get(play_type_url)).data
    let play_type_list = []//await parse_play_type_html(play_type_html)

    // 获取歌手页面内容
    let singer_type_url = host + "/singers/index/index/1.html"
    // console.log(url_serch)
    let singer_type_html = (await axios_1.default.get(singer_type_url)).data
    let singer_type_list = await parse_singer_type_html(singer_type_html)

    //合并歌单列表和歌手列表
    let merger_list = singer_type_list;
    for(let i=0; i<play_type_list.length; i++)
    {
        merger_list.push(play_type_list[i])
    }
    return merger_list;
}

async function searchMusic(query, page) {
    console.log("searchMusic enable_plugin=", enable_plugin)
    if(!enable_plugin)
    {
        console.log("无效的Token, 本插件已禁用。")
        return;
    }

    let key_word = encodeURIComponent(query)
    let url_serch = host + "/so.php?wd=" + key_word
    // console.log(url_serch)
    let search_res = (await axios_1.default.get(url_serch)).data
    // console.log(search_res)
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
        url: host+"/plug/down.php?ac=lrc&id=" + musicItem.id,
        timeout: 10000,
        // responseType:'txt',
    })).data;
    res = res.substring(34)
    res = res.replace("90T8", '****');  //屏蔽歌词中的网站信息
    res = res.replace("90听音乐网", '');  
    res = res.replace("44h4", '****'); 
    res = res.replace("欢迎来访", '');

    // console.log("getLyric:", res)
    return {
        rawLrc: res
    };
}


async function getTopLists() {
    if(!enable_plugin)
    {
        console.log("无效的Token, 本插件已禁用。")
        return;
    }
        
    const raw_html = (await axios_1.default.get(host + "/list/top.html")).data
    let toplist = await parse_top_list_html(raw_html)

    return [{
        title: "热门榜单",
        data: (toplist.hot_list).map((_) => {
            return ({
                id: _.id,
                coverImg: _.coverImg,
                title: _.title,
                description: _.description,
            });
        }),
    }, 
    {
        title: "特色音乐",
        data: (toplist.spectial_list).map((_) => {
            return ({
                id: _.id,
                coverImg: _.coverImg,
                title: _.title,
                description: _.description,
            });
        }),
    },
    {
        title: "全球榜单",
        data: (toplist.global_list).map((_) => {
            return ({
                id: _.id,
                coverImg: _.coverImg,
                title: _.title,
                description: _.description,
            });
        }),
    }];
}

async function getTopListDetail(topListItem) {

    let url_serch = host + topListItem.id
    // console.log(url_serch)
    let search_res = (await axios_1.default.get(url_serch)).data
    let song_list = await parse_play_list_html(search_res, "《")

    let res =  {
        ...topListItem,
        musicList: song_list.map((_) => {
            return {
                id: _.id,
                title: _.title,
                artist: _.artist,
                album: undefined,
                albumId: undefined,
                artistId: undefined,
                formats: undefined,
            };
        }),
    };
    return res;
}

async function getMusicSheetResponseById(sheet, page, pagesize = 50) {
    let separator;// 分隔符
    let bexchange = false;  //歌手、歌名交换位置
    // console.log('getMusicSheetResponseById, ',sheet)
    let play_list=[]
    if(sheet.sign === "singer")
    {
        separator = "《"
        let sheet_id = decodeURIComponent(sheet.id)
        sheet_id = sheet_id.replace("/1.html", "")
        let _play_list = []
        for(let idx=0; idx<=1; idx++)
        {
            let url_serch = host + sheet_id + `/${idx+1}.html`
            let raw_html = (await axios_1.default.get(url_serch)).data
            _play_list[idx] = await parse_play_list_html(raw_html, separator)
        }
        play_list = [..._play_list[0], ..._play_list[1]];
    }
    else
    {
        separator = "《"
        // bexchange = true
        let sheet_id = decodeURIComponent(sheet.id)
        let raw_html = (await axios_1.default.get(host + sheet_id)).data
        play_list = parse_play_list_html(raw_html, separator, bexchange)
    }
    
    return play_list;
}

async function getRecommendSheetTags() {
    let song_list = await get_play_Sheet_Tags()
    // console.log(res)
    const data = song_list
        .map((group) => ({
        title: group.name,
        data: group.data.map((_) => ({
            id: encodeURIComponent(_.id),
            digest: _.digest,
            title: _.title,
            sign: _.sign
        })),
    }));

    //固定的歌单标签
    const pinned = [
        {
            id: encodeURIComponent("/singers/huayu/index/1.html"),
            title: "华语歌手",
            digest: "fixed",
            sign: "singer"
        },
        {
            id: encodeURIComponent("/singers/hanguo/index/1.html"),
            title: "韩国歌手",
            digest: "fixed",
            sign: "singer"
        },
        {
            title: "欧美歌手",
            digest: "fixed",
            sign: "singer",
            id: encodeURIComponent("/singers/oumei/index/1.html"),
        },
    ];
    return {
        data,
        pinned,
    };
}

async function getRecommendSheetsByTag(tag, page) {
    // console.log("getRecommendSheetsByTag tag = ",tag)
    const pageSize = 20;
    let res;
    if (tag.id) {
        // 全部歌单
        res = (await axios_1.default.get(host + decodeURIComponent(tag.id))).data;
    }
    else {
        // 默认歌单
        res = (await axios_1.default.get(host+"/singers/index/index/1.html")).data;
    }

    let song_list_res
    // if(tag.sign === "singer")
    // {
        song_list_res = parse_singer_list_html(res)// 歌单列表
    // }
    // else
    // {
        // song_list_res = parse_song_list_html(res)// 歌单列表
    // }
    
    
    // const isEnd = page * pageSize >= res.total;
    return {
        isEnd: true,
        data: (await song_list_res).list.map((_) => ({
            title: _.name,
            artist: _.uname,
            id: encodeURIComponent(_.id),
            artwork: _.img,
            playCount: _.listencnt,
            createUserId: _.uid,
            sign: _.sign
        })),
    };
}

async function getMediaDownloadUrl(musicItem, quality){
    let _header = {
        'Referer': host + `/mp3/${musicItem}.html`,
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; Moto G (4)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Mobile Safari/537.36 Edg/89.0.774.68',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.9',
        'Cookie':'down_mima=ok',
        'Connection':'keep-alive',
        "Content-Type": "application/x-www-form-urlencoded",
    }

    let _url = host + `/plug/down.php?ac=music&id=${musicItem.id}`
    // console.log("---------------------_url: ", _url)
    // console.log("---------------------_header: ", _header)

    let mp3_Result = await fetch(_url, {
        method: 'get',
        headers: _header,
    });

    // console.log("---------------------search from third: ", mp3_Result.url)
    return  mp3_Result.url
}


async function getMediaSource(musicItem, quality) {
    // 90t8.com获取音源
    let req_url = host + `/mp3/${musicItem.id}.html`
    let mp3_Result = (await (0, axios_1.default)({
        url: req_url,
        method: 'get',
        timeout: 3000,
    })).data;
    // console.log("search from third: ", mp3_Result)
    if(mp3_Result)
    {
        const $ = cheerio_1.load(mp3_Result);
        let raw_lrc = $("div.gc").text();
        // let raw_url_html = $("div.container").find("script").text().match(/url:"(.*?).mp3"/)
        let raw_artwork = $("div.playhimg").find("img").attr("src");
        let raw_url = ''
        
        // if(raw_url_html === null)
        // {
            raw_url = await getMediaDownloadUrl(musicItem, quality)
        // }
        // else
        // {
        //     raw_url = raw_url_html[1] + ".mp3"
        // }

        if(raw_url !== null)
        {
            raw_lrc = raw_lrc.replace("90T8", '****');  //屏蔽歌词中的网站信息
            raw_lrc = raw_lrc.replace("44h4", '****'); 
            raw_lrc = raw_lrc.replace("90听音乐网", '');  //屏蔽歌词中的网站信息
        
            music_info = {
                url: raw_url,
                rawLrc: raw_lrc,
                artwork: raw_artwork,
            };
            return music_info;
        }
    }
    return {
        url: ""
    };
}

async function getMusicSheetInfo(sheet, page) {
    // console.log("getMusicSheetInfo, sheet = ", sheet)
    const res = await getMusicSheetResponseById(sheet, page, pageSize);
    return {
        isEnd: true,
        musicList: res.map((_) => ({
            id: _.id,
            title: _.title,
            artist: _.artist,
            album: undefined,
            albumId: undefined,
            artistId: undefined,
            formats: undefined,
        })),
    };
}

async function getMusicInfo(musicItem) {
    let req_url = host + `/mp3/${musicItem.id}.html`
    let mp3_Result = (await (0, axios_1.default)({
        url: req_url,
        method: 'get',
        timeout: 3000,
    })).data;
    // console.log("search from third: ", mp3_Result)

    const $ = cheerio_1.load(mp3_Result);
    let raw_artwork = $("div.playhimg").find("img").attr("src");

    return {
        artwork: raw_artwork,
    };
}

// 获取token，并根据token的有效性，开启或关闭本插件
get_plugin_token()
module.exports = {
    platform: plugin_name,
    version: "0.1.16",
    appVersion: ">0.1.0-alpha.0",
    author: "Vale",
    order: 19,
    srcUrl: "https://agit.ai/vale_gtt/MSC_API/raw/branch/master/my_plugins/third_party/my_kg_90t8.js",
    cacheControl: "no-cache",
    hints: {
        importMusicSheet: [],
    },

    async search(query, page, type) {
        // console.log("search(query, page, type): ", query, page, type)
        if (type === "music") {
            return await searchMusic(query, page);  //搜索歌曲
        }
    },

    // 获取音乐信息，分为三步
    getMusicInfo,   // 获取音乐所有信息
    getMediaSource, // 获取音源连接
    getLyric,       // 获取歌词

    getTopLists,            // 获取榜单
    getTopListDetail,       // 获取榜单详细内容
    getRecommendSheetTags,
    getRecommendSheetsByTag,
    getMusicSheetInfo,
    
};

// searchMusic("天地龙鳞").then(console.log)
// getLyric()
// getTopLists().then(console.log)
// getRecommendSheetTags()

// let music_item_1 = {
//       id: '5fa340b158c2e385e64338177384cfd7',
//       songmid: undefined,
//       title: '圣诞星 (feat. 杨瑞代)',
//       artist: '周杰伦',
//       artwork: undefined,
//       album: undefined,
//       lrc: undefined,
//       albumid: undefined,
//       albummid: undefined
//     }
// let music_item_3 = {
//         id: '8713d87a910907aa125cb9ac95e36270',
//         songmid: undefined,
//         title: '天地龙鳞',
//         artist: '王力宏',
//         artwork: undefined,
//         album: undefined,
//         lrc: undefined,
//         albumid: undefined,
//         albummid: undefined
//       }
// getLyric(music_item_1)
// let music_item_2 = {
//       id: '10986b847f4ddb6f42041b426f7756eb',
//       songmid: undefined,
//       title: '圣诞星 (改编版)',
//       artist: '大力滴滴滴',
//       artwork: undefined,
//       album: undefined,
//       lrc: undefined,
//       albumid: undefined,
//       albummid: undefined
//     }
// getMediaSource(music_item_3).then(console.log)
// getMediaDownloadUrl(music_item_2)
// let top_item={
//     id: "/list/kugou.html",
//     coverImg: undefined,
//     title: "酷狗飙升榜",
//     description: "每日同步官方数据。",
// }

// getTopListDetail(top_item).then(console.log)
// getRecommendSheetTags().then(console.log)


// let tag = {
//     id: '/singers/huayu/index/1.html', 
//     title: '华语歌手', 
//     digest: "singer" ,
//     sign: "singer"
// }

// let tag1 = {
//     id: '/gdlist/jlhou/1.html', 
//     title: '90', 
//     digest: "song" 
// }

// getRecommendSheetsByTag(tag).then(console.log)


// let singer = 
// {
//     title: '周杰伦',
//     artist: undefined,
//     id: '/singer/3520/1.html',
//     artwork: 'http://singerimg.kugou.com/uploadpic/softhead/400/20230510/20230510173043311.jpg',
//     playCount: undefined,
//     createUserId: undefined,
//     sign: 'singer'
//   }


// getMusicSheetInfo(singer, 0).then(console.log)

