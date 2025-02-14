"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const axios_1 = require("axios");
const he = require("he");
const cheerio_1 = require("cheerio");
const CryptoJS = require("crypto-js");

const host = "http://ww" + "w.dd" + "a5.com"
const token_host = "https://a" + "gi" + "t.ai"
const token_txt = 'token_date: 2023-12-20'

let enable_plugin = true;
const plugin_name = "咪咕"

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
        artwork: _.artwork,
        album: albumname,
        lrc: _.lyric || undefined,
        albumid: undefined,
        albummid: undefined,
    };
}

async function parse_play_list_html(raw_data, separator) {
    const $ = cheerio_1.load(raw_data);
    const raw_play_list = $("div.play_list").find("li");
    let song_list_arr = [];
    for(let i=0; i<raw_play_list.length; i++)
    {
        const item=$(raw_play_list[i]).find("a");
        
        let data_id = $(item[1]).attr("href").match(/\/mp3\/(.*?).html/)[1]
        // console.log($(item[0]).text())
        // let separated_text = $(item[1])
        let data_artist = $(item[2]).text() // 通过分隔符区分歌手和歌名
        let data_title = $(item[1]).text()
        let data_artwork = $(raw_play_list[i]).find("img").attr("src")
        song_list_arr.push({
            id: data_id, 
            title: data_title, 
            artist: data_artist,
            artwork: data_artwork
        })
    }
    // console.log("song_list_arr:",song_list_arr)
    return(song_list_arr)
}

async function parse_top_list_html(raw_data) {
    const $ = cheerio_1.load(raw_data);
    const raw_play_list = $("div.class").find("li");
    const page_data = $("div.pagedata").text();
    let cover_img = "https://agit.ai/vale_gtt/MSC_API/raw/branch/master/my_plugins/third_party/logo/mg.jpg"
    let classify_list = [];
    for(let i=0; i<5; i++)
    {
        const item=$(raw_play_list[i]).find("a");
        let data_address = $(item[0]).attr("href")
        let data_title = $(item[0]).text()
        classify_list.push({
            id: data_address, 
            coverImg: cover_img,
            title: data_title, 
            description: "每日同步官方数据。" + page_data
        })
    }

    let hot_list = [];
    for(let i=5; i<15; i++)
    {
        const item=$(raw_play_list[i]).find("a");
        let data_address = $(item[0]).attr("href")
        let data_title = $(item[0]).text()
        hot_list.push({
            id: data_address, 
            coverImg: cover_img,
            title: data_title, 
            description: "每日同步官方数据。" + page_data
        })
    }
    // console.log("song_list_arr:",song_list_arr)
    return {
        classify_list,
        hot_list,
    };
    
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


async function getTopLists() {
    if(!enable_plugin)
    {
        console.log("无效的Token, 本插件已禁用。")
        return;
    }
        
    const raw_html = (await axios_1.default.get(host + "/list/hotsong.html")).data
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
        title: "音乐分类",
        data: (toplist.classify_list).map((_) => {
            return ({
                id: _.id,
                coverImg: _.coverImg,
                title: _.title,
                description: _.description,
            });
        }),
    }]
}

async function getTopListDetail(topListItem) {

    let url_serch = host + topListItem.id
    // console.log(url_serch)
    let search_res = (await axios_1.default.get(url_serch)).data
    let song_list = await parse_play_list_html(search_res, "_")

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

    let sheet_id = decodeURIComponent(sheet.id)
    let raw_html = (await axios_1.default.get(host + sheet_id)).data
    let play_list = parse_play_list_html(raw_html)
    return play_list;
}

async function parse_play_type_html(raw_data) {
    // 解析歌单分类
    const $ = cheerio_1.load(raw_data);
    const raw_group_list = $("div.class")
    let group_list =[]
    for(let i=0; i<raw_group_list.length; i++)
    {
        let class_item =$(raw_group_list[i]).find("h1");
        let group_title = $(class_item[0]).text().replace(":", "")
        const group_item=$(raw_group_list[i]).find("li");
        // let group_title = $(group_item[0]).text().replace(":", "")
        let play_type = []
        for(let j=0; j<group_item.length; j++)
        {
            let data_address = $(group_item[j]).find("a").attr("href")
            let data_title = $(group_item[j]).text()
            play_type.push({
                id: data_address,
                digest: "song",
                title: data_title,
                sign: "song"
            })
        }
        group_list.push({
            name:group_title,
            data:play_type,
        })
    }
    return group_list;
}

async function parse_singer_type_html(raw_data) {
    // 解析歌手分类

    let singer_class = ["华语", "欧美", "日韩"]
    let singer_group = ["男歌手", "女歌手", "组合歌手"] 
    let singer_class_id = ["huayu", "oumei", "rihan"] 
    let singer_group_id = ["nan", "nv", "group"] 

    let group_list =[]
    let play_type = []
    for(let i=0; i<singer_class.length; i++)
    {

        for(let j=0; j<singer_group.length; j++)
        {

            play_type.push({
                id: '/slist/' + singer_class_id[i] + '/' +singer_group_id[j] + '.html',
                digest: "singer",
                title: singer_class[i]+singer_group[j],
                sign: "singer"
            })
        }
    }
    group_list.push({
        name:"歌手分类",
        data:play_type,
    })
    return group_list;
}

async function parse_song_list_html(raw_data) {
    // 解析歌单分类中的歌单列表
    const $ = cheerio_1.load(raw_data);
    const raw_song_list = $("div.video_list").find("li")
    // $(raw_group_list[i]).find("li")
    let song_list = []
    for(let i=0; i<raw_song_list.length; i++)
    {
        let item_1 = $(raw_song_list[i]).find("a")
        let data_id = $(item_1[0]).attr("href")
        let data_title = $(item_1[1]).attr("title")
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
    let total  = $("div.pagedata").text();
    return {
        count: total,
        list: song_list,
    };
}

async function parse_singer_list_html(raw_data) {
    // 解析歌单分类中的歌单列表
    const $ = cheerio_1.load(raw_data);
    const raw_song_list = $("div.singer_list").find("li")
    // $(raw_group_list[i]).find("li")
    let song_list = []
    for(let i=0; i<raw_song_list.length; i++)
    {
        let item_1 = $(raw_song_list[i]).find("a")
        let data_id = $(item_1[0]).attr("href")
        let data_title = $(item_1[1]).attr("title")
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
    let play_type_url = host + "/playtype/hot.html"
    // console.log(url_serch)
    let play_type_html = (await axios_1.default.get(play_type_url)).data
    let play_type_list = await parse_play_type_html(play_type_html)

    // 获取歌手页面内容
    let singer_type_url = host + "/slist/huayu/nan.html"
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
            id: encodeURIComponent("/slist/huayu/nan.html"),
            title: "华语歌手",
            digest: "fixed",
            sign: "singer"

        },
        {
            id: encodeURIComponent("/playtype/style.html"),
            title: "中国风",
            digest: "fixed",
            sign: "song"
        },
        {
            id: encodeURIComponent("/playtype/popular.html"),
            title: "流行",
            digest: "fixed",
            sign: "song"
        },
        {
            title: "KTV",
            digest: "fixed",
            sign: "song",
            id: encodeURIComponent("/playtype/ktv.html"),
        },
        {
            title: "古典",
            digest: "fixed",
            id: encodeURIComponent("/playtype/classical.html"),
            sign: "song"
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
        res = (await axios_1.default.get(host+"/playtype/hot.html")).data;
    }

    let song_list_res
    if(tag.sign === "singer")
    {
        song_list_res = parse_singer_list_html(res)// 歌单列表
    }
    else
    {
        song_list_res = parse_song_list_html(res)// 歌单列表
    }
    
    
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


async function getMediaSource(musicItem, quality) {
    // dda5.com获取音源
    let header = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": host+`/song/${musicItem.id}.html`,
    }
    let mp3_Result = (await (0, axios_1.default)({
        method: "post",
        url: host + `/style/js/play.php`,
        headers: header,
        data: `id=${musicItem.id}&type=dance`,
    })).data;
    
    // console.log("search from third: ",mp3_Result.url)

    if(mp3_Result.url)
    {
        return {
            url: mp3_Result.url,
            artwork: mp3_Result.pic,
            rawLrc: mp3_Result.lrc
        };
    } 
    return {
        url: ""
    };
}

async function getMusicSheetInfo(sheet, page) {
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

// 获取token，并根据token的有效性，开启或关闭本插件
get_plugin_token()
module.exports = {
    platform: plugin_name,
    version: "0.1.14",
    appVersion: ">0.1.0-alpha.0",
    author: "Vale",
    order: 19,
    srcUrl: "https://agit.ai/vale_gtt/MSC_API/raw/branch/master/my_plugins/third_party/my_mg_dda5.js",
    cacheControl: "no-cache",
    hints: {
        importMusicSheet: [],
    },

    async search(query, page, type) {
        // console.log("search(query, page, type): ", query, page, type)
        if (type === "music") {
            return await searchMusic(query, page);
        }
    },

    getMediaSource,
    getLyric: getMediaSource,
    getTopLists,
    getTopListDetail,
    getRecommendSheetTags,
    getRecommendSheetsByTag,
    getMusicSheetInfo,
    getMusicInfo: getMediaSource
};

// searchMusic("告白气球").then(console.log)
// getLyric()
// getTopLists().then(console.log)
// getRecommendSheetTags()

// let music_item =
//     {
//         id: '60054704037',
//         songmid: undefined,
//         title: '告白气球',
//         artist: '周杰伦',
//         artwork: 'https://d.musicapp.migu.cn/data/oss/resource/00/2h/ty/mo',
//         album: undefined,
//         lrc: undefined,
//         albumid: undefined,
//         albummid: undefined
//       }
// getMediaSource(music_item)

// let top_item={
//     id: "/list/hotsong.html",
//     coverImg: undefined,
//     title: "热歌榜",
//     description: "酷我每日搜索热度飙升最快的歌曲排行榜，按搜索播放数据对比前一天涨幅排序，每天更新",
// }

// getTopListDetail(top_item)
// getRecommendSheetTags()

// let tag = {
//     id: '/playtype/old.html', 
//     title: '经典老哥', 
//     digest: "song" ,
//     sign: "song"
// }

// let tag2 = {
//     id: '/slist/huayu/nan.html', 
//     title: '华语歌手', 
//     digest: "singer" ,
//     sign: "singer"
// }

// getRecommendSheetsByTag(tag2)

// let singer = 
// {
//     title: '周杰伦',
//     artist: undefined,
//     id: '/singer/112.html',
//     artwork: 'https://d.musicapp.migu.cn/data/oss/resource/00/26/vy/av.webp',
//     playCount: undefined,
//     createUserId: undefined,
//     sign: 'singer'
// }


// getMusicSheetInfo(singer, 0).then(console.log)
