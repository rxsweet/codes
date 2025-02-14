"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const axios_1 = require("axios");
const he = require("he");
const cheerio_1 = require("cheerio");
const CryptoJS = require("crypto-js");

const host = "http://ww" + "w.33" + "z3.com"
const token_host = "https://a" + "gi" + "t.ai"
const token_txt = 'token_date: 2023-12-20'
const plugin_name = "QQ音乐"

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
    const raw_play_list = $("div.ilingku_musiclist").find("li");
    let song_list_arr = [];
    for(let i=0; i<raw_play_list.length; i++)
    {
        const item=$(raw_play_list[i]).find("a");
        
        let data_id = $(item[1]).attr("href").match(/\/play\/(.*?).html/)[1]
        // console.log($(item[0]).text())
        // let separated_text = $(item[0]).text().split(separator)
        let aaa = $($(raw_play_list[i]).find("p")).text()
        let data_artist = $($(raw_play_list[i]).find("p")).text().replaceAll(' ','').match(/\n\t\t\t\t\t(.*?)\t\t\t\t\t\t/)[1]
        let data_title = $(item[1]).text()
        data_artist = data_artist.replace('\t','')
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
    const raw_play_list = $("div.class").find("li");
    const page_data = '' //$($($("div.main")[0]).find("div")[1]).text();
    let cover_img = "https://agit.ai/vale_gtt/MSC_API/raw/branch/master/my_plugins/third_party/logo/qq.jpg"
    let hot_list = [];
    for(let i=0; i<12; i++)
    {
        const item=$(raw_play_list[i]).find("a");
        let data_address = $(item[0]).attr("href")
        let data_title = $(item[0]).text()
        // data_title = data_title.replace('TOP排行榜','酷狗TOP500')
        hot_list.push({
            id: data_address, 
            coverImg: cover_img,
            title: data_title, 
            description: "每日同步官方数据。" + page_data
        })
    }
    let spectial_list = []
    for(let i=12; i<24; i++)
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
    let recommend_list = []
    for(let i=24; i<raw_play_list.length; i++)
    {
        const item=$(raw_play_list[i]).find("a");
        let data_address = $(item[0]).attr("href")
        let data_title = $(item[0]).text()
        recommend_list.push({
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
        recommend_list
    };}

async function parse_play_type_html(raw_data) {
    // 解析歌单分类
    const $ = cheerio_1.load(raw_data);
    const raw_group_list = $("div.gdclass")
    let group_list =[]
    for(let i=0; i<raw_group_list.length; i++)
    {
        const group_item=$(raw_group_list[i]).find("li");
        let group_title = $($(raw_group_list[i]).find("h1")).text()
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
    const $ = cheerio_1.load(raw_data);
    const raw_group_list = $("div.gsclass")
    let group_list =[]
    for(let i=0; i<1; i++)
    {
        const group_item=$(raw_group_list[i]).find("li");
        let group_title = $($(raw_group_list[i]).find("h1")).text()
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
    const raw_song_list = $("div.ilingku_piclist").find("li")
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
        let data_id = $(item_1[0]).attr("href").replace("/singer/", '/singer/song/')
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

    //合并歌单列表和歌手列表
    let merger_list = play_type_list;

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
    let song_list = await parse_play_list_html(search_res)

    const songs = song_list.map(formatMusicItem);

    return {
        isEnd: true,
        data: songs,
    };
}


async function getLyric(musicItem) {
    // console.log("getLyric:", musicItem)
    let header = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": host+`/play/${musicItem.id}.html`,
    }
    let mp3_Result = (await (0, axios_1.default)({
        method: "post",
        url: host + `/style/js/play.php`,
        headers: header,
        data: `id=${musicItem.id}&type=play`,
    })).data;
    // console.log("getLyric: ",mp3_Result.lrc)

    if(mp3_Result.lrc)
    {
        return {
            rawLrc: mp3_Result.lrc,
        };
    } 
}

async function getMusicInfo(musicItem) {
    let header = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": host+`/play/${musicItem.id}.html`,
    }
    let mp3_Result = (await (0, axios_1.default)({
        method: "post",
        url: host + `/style/js/play.php`,
        headers: header,
        data: `id=${musicItem.id}&type=play`,
    })).data;
    // console.log("getMusicInfo pic: ",mp3_Result.pic)

    if(mp3_Result.pic)
    {
        return {
            artwork: mp3_Result.pic,
        };
    } 
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
        title: "推荐榜单",
        data: (toplist.recommend_list).map((_) => {
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
        let url_search = host + topListItem_id + `/${idx+1}.html`
        // console.log(url_serch)
        let search_res = (await axios_1.default.get(url_search)).data
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
        // bexchange = true
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
            id: encodeURIComponent("/singerlist/gangtai/index/index/index.html"),
            title: "港台歌手",
            digest: "fixed",
            sign: "singer"
        },
        {
            id: encodeURIComponent("/playtype/liuxing.html"),
            title: "流行",
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
            title: "中国风",
            digest: "fixed",
            sign: "song",
            id: encodeURIComponent("/playtype/zgf.html"),
        },
        {
            title: "情歌",
            digest: "fixed",
            id: encodeURIComponent("/playtype/qingge.html"),
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
    // 33z3.com获取音源

    let _header = {
        "Referer": host + `/play/${musicItem.id}.html`,
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; Moto G (4)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Mobile Safari/537.36 Edg/89.0.774.68',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.9',
        'Cookie':'down_mima=ok',
        'Connection':'keep-alive',
        "Content-Type": "application/x-www-form-urlencoded",
        // 'host': host,
    }

    let _url = host + `/plug/down.php?ac=dmp3&id=${musicItem.id}&type=320`

    let mp3_Result = await fetch(_url, {
        method: 'get',
        headers: _header,
    });
    // console.log("search from third: ",mp3_Result.url)

    if(mp3_Result.url)
    {
        return {
            url: mp3_Result.url,
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
    srcUrl: "https://agit.ai/vale_gtt/MSC_API/raw/branch/master/my_plugins/third_party/my_qq_33z3.js",
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
    getMusicInfo,
};

// searchMusic("告白气球").then(console.log)
// getLyric()
// getTopLists().then(console.log)
// getRecommendSheetTags().then(console.log)

// let music_item = 
// {
//     id: 'ZWZrZWprZmVoag',
//     songmid: undefined,
//     title: '告白气球',
//     artist: '周杰伦',
//     artwork: undefined,
//     album: undefined,
//     lrc: undefined,
//     albumid: undefined,
//     albummid: undefined
// };
// getMediaSource(music_item)
// getLyric(music_item)
// getMusicInfo(music_item)

// let top_item={
//     id: "/list/top.html",
//     coverImg: undefined,
//     title: "top热歌榜",
//     description: "每日搜索热度飙升最快的歌曲排行榜，按搜索播放数据对比前一天涨幅排序，每天更新",
// }

// getTopListDetail(top_item)

// let tag = {
//     id: encodeURIComponent('/singerlist/huayu/index/index/index.html'), 
//     title: '华语歌手', 
//     digest: "singer" ,
//     sign: "singer"
// }

// let tag1 = {
//     id: encodeURIComponent('/playtype/liuxing.html'), 
//     title: '流行', 
//     digest: "song" 
// }

// let tag2 = {
//     title: '默认', 
//     // digest: "singer" 
// }
// // getRecommendSheetsByTag(tag1).then(console.log)


// let singer = 
// {
//     title: '周杰伦',
//     artist: undefined,
//     id: encodeURIComponent('/singer/song/hlN2yWrP4s0025N.html'),
//     artwork: 'http://tu.eev3.com/t.php?h=100&w=100&url=http://img1.kuwo.cn/star/starheads/300/8/10/2150960774.jpg',
//     playCount: undefined,
//     createUserId: undefined,
//     sign: 'singer'
// }

// let song = 
// {
//     title: '长月烬明',
//     artist: undefined,
//     id: encodeURIComponent('/playlist/d3Zld3Z5d2h2bms.html'),
//     artwork: 'http://tu.eev3.com/t.php?h=100&w=100&url=http://img1.kuwo.cn/star/starheads/300/8/10/2150960774.jpg',
//     playCount: undefined,
//     createUserId: undefined,
//     sign: 'song'
// }


// getMusicSheetInfo(song, 0).then(console.log)
