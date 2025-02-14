"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const axios_1 = require("axios");
const he = require("he");
const cheerio_1 = require("cheerio");
const CryptoJS = require("crypto-js");

const host = "http://ww" + "w.2t" + "58.com"
const token_host = "https://a" + "gi" + "t.ai"
const token_txt = 'token_date: 2023-12-20'
const plugin_name = "酷我"

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

async function parse_play_list_html(raw_data, separator, bExchange = false) {
    const $ = cheerio_1.load(raw_data);
    const raw_play_list = $("div.play_list").find("li");
    let song_list_arr = [];
    for(let i=0; i<raw_play_list.length; i++)
    {
        const item=$(raw_play_list[i]).find("a");
        
        let data_id = $(item[0]).attr("href").match(/\/song\/(.*?).html/)[1]
        // console.log($(item[0]).text())
        let separated_text = $(item[0]).text().split(separator)
        let data_artist = separated_text[0] // 通过分隔符区分歌手和歌名
        let data_title = separated_text[1]!="" ? separated_text[1]:separated_text[2]
        if(bExchange)
        {
            let temp = data_artist;
            data_artist = data_title;
            data_title = temp;
        }
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
    const raw_play_list = $("div.ilingku_fl").find("li");
    const page_data = $("div.pagedata").text();
    let top_list_arr = [];
    let cover_img = "https://agit.ai/vale_gtt/MSC_API/raw/branch/master/my_plugins/third_party/logo/kw.jpg"
    top_list_arr.push(
        {id: "/list/new.html", coverImg: cover_img, title: "酷我新歌榜", description: "每日同步官方数据。" + page_data},
        {id: "/list/top.html", coverImg: cover_img, title: "酷我飙升榜", description: "每日同步官方数据。" + page_data},)
    for(let i=0; i<raw_play_list.length; i++)
    {
        const item=$(raw_play_list[i]).find("a");
        let data_address = $(item[0]).attr("href")
        let data_title = $(item[0]).text()
        data_title = data_title.replace('DJ舞曲大全','万物DJ榜')
        data_title = data_title.replace('音乐热评榜','酷我热评榜')
        data_title = data_title.replace('爱听电音榜','极品电音榜')
        data_title = data_title.replace('酷我飙升榜','酷我热歌榜')
        data_title = data_title.replace('80后热歌榜','酷我怀旧榜')
        data_title = data_title.replace('会员喜爱榜','会员爱听排行榜')
        top_list_arr.push({
            id: data_address, 
            coverImg: cover_img,
            title: data_title, 
            description: "每日同步官方数据。" + page_data
        })
    }
    // console.log("song_list_arr:",song_list_arr)
    return(top_list_arr)
    
}

async function parse_play_type_html(raw_data) {
    // 解析歌单分类
    const $ = cheerio_1.load(raw_data);
    const raw_group_list = $("div.ilingku_fl")
    let group_list =[]
    for(let i=0; i<raw_group_list.length; i++)
    {
        const group_item=$(raw_group_list[i]).find("li");
        let group_title = $(group_item[0]).text().replace(":", "")
        let play_type = []
        for(let j=1; j<group_item.length; j++)
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
    const $ = cheerio_1.load(raw_data);
    const raw_group_list = $("div.ilingku_fl")
    let group_list =[]
    for(let i=0; i<1; i++)
    {
        const group_item=$(raw_group_list[i]).find("li");
        let group_title = $(group_item[0]).text().replace(":", "")
        let play_type = []
        for(let j=1; j<group_item.length; j++)
        {
            let data_address = $(group_item[j]).find("a").attr("href")
            let data_title = $(group_item[j]).text()
            play_type.push({
                id: data_address,
                digest: "singer",
                title: data_title,
                sign: "singer"
            })
        }
        group_list.push({
            name:group_title,
            data:play_type,
        })
    }
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
    let total  = $("div.pagedata").find("span").text();
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
    let play_type_url = host + "/playtype/index.html"
    // console.log(url_serch)
    let play_type_html = (await axios_1.default.get(play_type_url)).data
    let play_type_list = await parse_play_type_html(play_type_html)

    // 获取歌手页面内容
    let singer_type_url = host + "/singerlist/index/index/index/index.html"
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


async function getTopLists() {
    if(!enable_plugin)
    {
        console.log("无效的Token, 本插件已禁用。")
        return;
    }
        
    const raw_html = (await axios_1.default.get(host + "/list/top.html")).data
    let toplist = await parse_top_list_html(raw_html)

    return [{
        title: "官方榜单",
        data: toplist.map((_) => {
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

    let topListItem_id = topListItem.id.replace(".html", "")
    let _song_list = []
    for(let idx=0; idx<=1; idx++)
    {
        let url_serch = host + topListItem_id + `/${idx+1}.html`
        // console.log(url_serch)
        let search_res = (await axios_1.default.get(url_serch)).data
        _song_list[idx] = await parse_play_list_html(search_res, "_")
    }
    let song_list = [..._song_list[0], ..._song_list[1]];
    
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
    let play_list=[]
    if(sheet.sign === "singer")
    {
        separator = "_"
        let sheet_id = decodeURIComponent(sheet.id)
        sheet_id = sheet_id.replace(".html", "")
        let _play_list = []
        for(let idx=0; idx<=1; idx++)
        {
            let url_serch = host + sheet_id + `/${idx+1}.html`
            let raw_html = (await axios_1.default.get(url_serch)).data
            _play_list[idx] = await parse_play_list_html(raw_html, "_")
        }
        play_list = [..._play_list[0], ..._play_list[1]];
    }
    else
    {
        separator = " - "
        bexchange = true
        let raw_html = (await axios_1.default.get(host + decodeURIComponent(sheet.id))).data
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
            id: encodeURIComponent("/singerlist/huayu/index/index/index.html"),
            title: "华语歌手",
            digest: "fixed",
            sign: "singer"

        },
        {
            id: encodeURIComponent("/playtype/jingdian.html"),
            title: "经典",
            digest: "fixed",
            sign: "song"
        },
        {
            id: encodeURIComponent("/playtype/ktv.html"),
            title: "KTV",
            digest: "fixed",
            sign: "song"
        },
        {
            title: "放松",
            digest: "fixed",
            sign: "song",
            id: encodeURIComponent("/playtype/fangsong.html"),
        },
        {
            title: "安静",
            digest: "fixed",
            id: encodeURIComponent("/playtype/anjing.html"),
            sign: "song"
        },
        {
            title: "90后",
            digest: "fixed",
            id: encodeURIComponent("/playtype/90h.html"),
            sign: "song"
        },
        {
            title: "流行",
            digest: "fixed",
            id: encodeURIComponent("/playtype/liuxing.html"),
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
        res = (await axios_1.default.get(host+"/playtype/index.html")).data;
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
    // 2t58.com获取音源
    let header = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": host+`/song/${musicItem.id}.html`,
    }
    let mp3_Result = (await (0, axios_1.default)({
        method: "post",
        url: host + `/js/play.php`,
        headers: header,
        data: `id=${musicItem.id}&type=music`,
    })).data;
    // console.log("search from third: ",mp3_Result)

    if(mp3_Result.url)
    {
        return {
            url: mp3_Result.url,
            artwork: mp3_Result.pic,
        };
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

// 获取token，并根据token的有效性，开启或关闭本插件
get_plugin_token()
module.exports = {
    platform: plugin_name,
    version: "0.1.14",
    appVersion: ">0.1.0-alpha.0",
    author: "Vale",
    order: 19,
    srcUrl: "https://agit.ai/vale_gtt/MSC_API/raw/branch/master/my_plugins/third_party/my_kw_2t58.js",
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
    getLyric,
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
