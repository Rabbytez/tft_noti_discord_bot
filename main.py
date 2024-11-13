import requests
import json

def get_profile_data(riotname, tag):
    
    file_name = f"output/v2-profile-data-{riotname}-{tag}.json"
    url = "https://mobalytics.gg/api/tft/v1/graphql/query"

    headers = {
        "Content-Type": "application/json",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en_us",
        "cookie": "appmobaabgroup=A; appcfcountry=TH;",
        "dnt": "1",
        "origin": "https://mobalytics.gg",
        "referer": f"https://mobalytics.gg/tft/profile/th/{riotname}-{tag}/overview",
        "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
    }

    body = {
        "operationName": "TftProfilePageQuery",
        "variables": {
            "bNormalFilter": {"queues": ["NORMAL"], "patches": []},
            "bRankedFilter": {"queues": ["RANKED"], "patches": []},
            "bHyperRollFilter": {"queues": ["HYPER_ROLL"], "patches": []},
            "lpGainsPerPage": 150,
            "filter": [
                {"gameName": riotname, "tagLine": tag, "region": "TH", "set": "12"}
            ],
            "filterStats": {
                "queue": None,
                "synergy": [],
                "champion": [],
                "patch": [],
                "dateFrom": None
            },
            "filterProgressTracking": {"queue": "RANKED"},
            "summonerProgressPerPageCount": 50,
            "filterRecentActivity": "2024-07-13T08:35:43.418Z",
            "statsOverviewLimit": 5,
            "statsSectionLimit": 20,
            "withSummonerInfo": True,
            "withSummonerPerformance": True,
            "withSummonerProgressTracking": True,
            "withOverviewSection": True,
            "withTeamCompsSection": False,
            "withStatsSection": False,
            "withLpGainsSection": False,
            "lpGainsPage": 1,
            "teamCompsArchetypeSize": 20
        },
        "query": "query TftProfilePageQuery($filter: [TftProfileFilter!], $bNormalFilter: TftBadgesFilter! = {queues: [NORMAL]}, $bRankedFilter: TftBadgesFilter! = {queues: [RANKED]}, $bHyperRollFilter: TftBadgesFilter! = {queues: [HYPER_ROLL]}, $badgesLimit: Int, $filterPerformance: [TftProfilePerformanceFilter!], $filterStats: TftProfileStatsFilter, $filterProgressTracking: TftProfileProgressTrackingFilterV3!, $summonerProgressPerPageCount: Int, $filterRecentActivity: TftDateTime, $statsOverviewLimit: Int, $statsSectionLimit: Int, $teamCompsArchetypeSize: Int, $withSummonerInfo: Boolean!, $withSummonerPerformance: Boolean!, $withSummonerProgressTracking: Boolean!, $withOverviewSection: Boolean!, $withTeamCompsSection: Boolean!, $withStatsSection: Boolean!, $withLpGainsSection: Boolean!, $lpGainsPerPage: Int = 150, $lpGainsPage: Int!) {\n  tft {\n    profile(filter: $filter) {\n      profile {\n        ...TftProfileFragment\n        __typename\n      }\n      error {\n        ...TftErrorFragment\n        ...TftInvalidParameterErrorFragment\n        ...TftSummonerNotFoundErrorFragment\n        ...TftNeedPremiumErrorFragment\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment TftProfileFragment on TftProfile {\n  puuid\n  set\n  rank {\n    ...TftSummonerRankFragment\n    __typename\n  }\n  info {\n    gameName\n    tagLine\n    __typename\n  }\n  badgesNormal: badges(filter: $bNormalFilter, limit: $badgesLimit) {\n    ...TftBadgeDynamicFragment\n    __typename\n  }\n  badgesRanked: badges(filter: $bRankedFilter, limit: $badgesLimit) {\n    ...TftBadgeDynamicFragment\n    __typename\n  }\n  badgesHyperRoll: badges(filter: $bHyperRollFilter, limit: $badgesLimit) {\n    ...TftBadgeDynamicFragment\n    __typename\n  }\n  ...TftProfileLeaderboardInfoFragment @include(if: $withSummonerInfo)\n  ...TftProfileSummonerInfoWithUpdateDataFragment @include(if: $withSummonerInfo)\n  ...TftProfileSummonerPerformanceFragment @include(if: $withSummonerPerformance)\n  summonerProgressTracking: progressTrackingV3(\n    filter: $filterProgressTracking\n    perPage: $summonerProgressPerPageCount\n  ) {\n    ...TftProfileSummonerProgressTrackingFragment @include(if: $withSummonerProgressTracking)\n    __typename\n  }\n  ...TftProfileSectionOverviewFragment @include(if: $withOverviewSection)\n  ...TftProfileSectionTeamCompsFragment @include(if: $withTeamCompsSection)\n  ...TftProfileSectionStatsFragment @include(if: $withStatsSection)\n  summonerLpGains: progressTrackingV3(\n    filter: $filterProgressTracking\n    page: $lpGainsPage\n    perPage: $lpGainsPerPage\n  ) {\n    ...TftProfileSummonerProgressTrackingFragment @include(if: $withLpGainsSection)\n    __typename\n  }\n  __typename\n}\n\nfragment TftSummonerRankFragment on SummonerRank {\n  tier\n  division\n  __typename\n}\n\nfragment TftProfileLeaderboardInfoFragment on TftProfile {\n  leaderboardStanding {\n    ...TftProfileLeaderboardStandingFragment\n    __typename\n  }\n  __typename\n}\n\nfragment TftProfileLeaderboardStandingFragment on TftLeaderboardStanding {\n  lp\n  regionPosition\n  __typename\n}\n\nfragment TftProfileSummonerInfoWithUpdateDataFragment on TftProfile {\n  summonerInfo: info {\n    ...TftSummonerFragmentWithMobauuid\n    updatedAt\n    isUpdating\n    __typename\n  }\n  __typename\n}\n\nfragment TftSummonerFragmentWithMobauuid on TftSummoner {\n  ...TftSummonerFragment\n  mobaUuid\n  __typename\n}\n\nfragment TftSummonerFragment on TftSummoner {\n  puuid\n  accountId\n  summonerId\n  gameName\n  tagLine\n  region\n  profileIcon\n  level\n  __typename\n}\n\nfragment TftProfileSummonerPerformanceFragment on TftProfile {\n  summonerPerformance: performance(filters: $filterPerformance) {\n    performance {\n      ...TftProfileQueuePerformanceFragment\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment TftProfileQueuePerformanceFragment on TftProfileQueuePerformance {\n  puuid\n  region\n  set\n  queue\n  rank {\n    ...TftSummonerRankFragment\n    __typename\n  }\n  games\n  averagePlace\n  averageRound\n  top1\n  stats {\n    placementDistribution {\n      ...TftProfilePlacementDistributionFragment\n      __typename\n    }\n    __typename\n  }\n  wins\n  losses\n  winrate\n  averageTimeEliminatedSeconds\n  damageDealt\n  lp\n  synergies {\n    ...TftProfileSynergiesFragment\n    __typename\n  }\n  chosens {\n    ...TftProfileChosenSynergiesFragment\n    __typename\n  }\n  champions {\n    ...TftProfileChampionsFragment\n    __typename\n  }\n  archetypes {\n    ...TftProfileArchetypesFragment\n    __typename\n  }\n  items {\n    ...TftProfileItemsFragment\n    __typename\n  }\n  __typename\n}\n\nfragment TftProfileSynergiesFragment on TftProfileSynergies {\n  items {\n    ...TftProfileSynergiesStatFragment\n    __typename\n  }\n  __typename\n}\n\nfragment TftProfileSynergiesStatFragment on TftProfileSynergyStat {\n  name\n  games\n  gamesGold\n  gamesSilver\n  gamesBronze\n  gamesChromatic\n  top4Games\n  top4Percent\n  averagePlace\n  lpGained\n  __typename\n}\n\nfragment TftProfileChosenSynergiesFragment on TftProfileChosenSynergies {\n  items {\n    ...TftProfileChosenSynergyStatFragment\n    __typename\n  }\n  __typename\n}\n\nfragment TftProfileChosenSynergyStatFragment on TftProfileChosenSynergyStat {\n  name\n  games\n  top4Games\n  top4Percent\n  averagePlace\n  __typename\n}\n\nfragment TftProfileChampionsFragment on TftProfileChampions {\n  items {\n    ...TftProfileChampionsStatFragment\n    __typename\n  }\n  __typename\n}\n\nfragment TftProfileChampionsStatFragment on TftProfileChampionStat {\n  name\n  games\n  top4Games\n  top4Percent\n  averagePlace\n  __typename\n}\n\nfragment TftProfileArchetypeStatFragment on TftProfileArchetypeStat {\n  formation {\n    ...TftProfileFormationFragment\n    __typename\n  }\n  games\n  top4Games\n  top4Percent\n  averagePlace\n  averageRound\n  averageTimeSeconds\n  lpGained\n  __typename\n}\n\nfragment TftProfileFormationFragment on TftProfileFormation {\n  units {\n    ...TftProfileUnitFragment\n    __typename\n  }\n  synergies {\n    ...TftProfileSynergyFragment\n    __typename\n  }\n  __typename\n}\n\nfragment TftProfileUnitFragment on TftProfileUnit {\n  slug\n  __typename\n}\n\nfragment TftProfileSynergyFragment on TftProfileSynergy {\n  slug\n  style\n  __typename\n}\n\nfragment TftProfileItemsFragment on TftProfileItems {\n  items {\n    ...TftProfileItemStatFragment\n    __typename\n  }\n  __typename\n}\n\nfragment TftProfileItemStatFragment on TftProfileItemStat {\n  name\n  games\n  top4Games\n  top4Percent\n  averagePlace\n  __typename\n}\n\nfragment TftProfilePlacementDistributionFragment on TftProfilePlacementDistribution {\n  items {\n    ...TftProfilePlacementDistributionItemFragment\n    __typename\n  }\n  __typename\n}\n\nfragment TftProfilePlacementDistributionItemFragment on TftProfilePlacementDistributionItem {\n  place\n  games\n  __typename\n}\n\nfragment TftProfileSummonerProgressTrackingFragment on TftProfileProgressTrackingV3 {\n  progress {\n    ...TftProfileQueueProgressFragment\n    __typename\n  }\n  error {\n    ...TftErrorFragment\n    __typename\n  }\n  __typename\n}\n\nfragment TftProfileQueueProgressFragment on TftProfileQueueProgressV3 {\n  entries {\n    ...TftProfileQueueProgressEntryFragment\n    __typename\n  }\n  thresholds {\n    ...TftProfileQueueProgressThresholdFragment\n    __typename\n  }\n  minValue\n  maxValue\n  pageInfo {\n    totalPages\n    totalItems\n    perPage\n    __typename\n  }\n  __typename\n}\n\nfragment TftProfileQueueProgressEntryFragment on TftProfileQueueProgressEntryV3 {\n  id\n  date\n  placement\n  patch\n  traits {\n    slug\n    numUnits\n    style\n    __typename\n  }\n  units {\n    chosen\n    items\n    slug\n    tier\n    __typename\n  }\n  lp {\n    after {\n      lp\n      rank {\n        tier\n        division\n        __typename\n      }\n      value\n      __typename\n    }\n    lpDiff\n    promoted\n    __typename\n  }\n  __typename\n}\n\nfragment TftProfileQueueProgressThresholdFragment on TftProfileQueueProgressTreshold {\n  tier\n  division\n  minLP\n  maxLP\n  minValue\n  maxValue\n  __typename\n}\n\nfragment TftErrorFragment on TftError {\n  message\n  __typename\n}\n\nfragment TftProfileSectionOverviewFragment on TftProfile {\n  overviewSection: stats(filter: $filterStats) {\n    patches {\n      patches\n      __typename\n    }\n    recentActivity: recentActivityV2(dateFrom: $filterRecentActivity) {\n      ...TftProfileRecentActivityFragment\n      __typename\n    }\n    placementDistribution {\n      ...TftProfilePlacementDistributionFragment\n      __typename\n    }\n    synergies(limit: $statsOverviewLimit) {\n      ...TftProfileSynergiesFragment\n      __typename\n    }\n    champions(limit: $statsOverviewLimit) {\n      ...TftProfileChampionsFragment\n      __typename\n    }\n    recentSummary {\n      ...TftProfileRecentSummaryFragment\n      __typename\n    }\n    matches {\n      ...TftMatchesInfiniteScrollFragment\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment TftProfileRecentActivityFragment on TftProfileRecentActivityV2 {\n  items {\n    ...TftProfileRecentActivityItemFragment\n    __typename\n  }\n  gamesPlayed\n  timePlayedSeconds\n  __typename\n}\n\nfragment TftProfileRecentActivityItemFragment on TftProfileRecentActivityV2Item {\n  date\n  timePlayedSeconds\n  gamesPlayed\n  wins\n  losses\n  winrate\n  __typename\n}\n\nfragment TftProfileRecentSummaryFragment on TftProfileRecentSummary {\n  games\n  placement\n  top1\n  top1Winrate\n  top4\n  top4Winrate\n  synergies {\n    ...TftProfileSynergiesFragment\n    __typename\n  }\n  items {\n    ...TftProfileItemsFragment\n    __typename\n  }\n  __typename\n}\n\nfragment TftMatchesInfiniteScrollFragment on TftMatchesInfiniteScroll {\n  items {\n    ...TftMatchRegistryFragment\n    __typename\n  }\n  pageInfo {\n    ...TftPageInfoFragment\n    __typename\n  }\n  __typename\n}\n\nfragment TftMatchRegistryFragment on TftMatchRegistry {\n  id: matchId\n  date\n  region\n  patch\n  queue\n  lp {\n    lpDiff\n    __typename\n  }\n  placement\n  durationSeconds\n  damageDealt\n  timeEliminatedSeconds\n  archetypeId\n  traits {\n    ...TftMatchRegistryTraitFragment\n    __typename\n  }\n  units {\n    ...TftMatchRegistryUnitFragment\n    __typename\n  }\n  placements {\n    ...TftMatchPlacementFragment\n    __typename\n  }\n  __typename\n}\n\nfragment TftMatchRegistryTraitFragment on TftMatchRegistryTrait {\n  slug\n  numUnits\n  style\n  tierCurrent\n  tierTotal\n  __typename\n}\n\nfragment TftMatchRegistryUnitFragment on TftMatchRegistryUnit {\n  slug\n  tier\n  items\n  chosen\n  __typename\n}\n\nfragment TftMatchPlacementFragment on TftMatchPlacement {\n  puuid\n  region\n  set\n  profile {\n    ...TftProfileNestedFragment\n    __typename\n  }\n  placement\n  __typename\n}\n\nfragment TftProfileNestedFragment on TftProfile {\n  puuid\n  rank {\n    ...TftSummonerRankFragment\n    __typename\n  }\n  ...TftProfileSummonerInfoFragment\n  __typename\n}\n\nfragment TftProfileSummonerInfoFragment on TftProfile {\n  puuid\n  summonerInfo: info {\n    ...TftSummonerFragment\n    __typename\n  }\n  __typename\n}\n\nfragment TftPageInfoFragment on TftInfiniteScrollPageInfo {\n  cursor\n  hasNextPage\n  totalItems\n  __typename\n}\n\nfragment TftProfileSectionTeamCompsFragment on TftProfile {\n  teamCompsSection: stats(filter: $filterStats) {\n    archetypes(limit: $teamCompsArchetypeSize) {\n      ...TftProfileArchetypesFragment\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment TftProfileArchetypesFragment on TftProfileArchetypes {\n  items {\n    ...TftProfileArchetypeStatFragment\n    __typename\n  }\n  __typename\n}\n\nfragment TftProfileSectionStatsFragment on TftProfile {\n  statsSection: stats(filter: $filterStats) {\n    synergies(limit: $statsSectionLimit) {\n      ...TftProfileSynergiesFragment\n      __typename\n    }\n    champions(limit: $statsSectionLimit) {\n      ...TftProfileChampionsFragment\n      __typename\n    }\n    items(limit: $statsSectionLimit) {\n      ...TftProfileItemsFragment\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment TftBadgeDynamicFragment on TftBadge {\n  slug\n  metadata {\n    ...TftBadgeDynamicMetadataFragment\n    __typename\n  }\n  __typename\n}\n\nfragment TftBadgeDynamicMetadataFragment on TftBadgeMetadata {\n  key\n  value\n  __typename\n}\n\nfragment TftInvalidParameterErrorFragment on TftInvalidParameterError {\n  message\n  parameter\n  __typename\n}\n\nfragment TftSummonerNotFoundErrorFragment on TftSummonerNotFoundError {\n  message\n  region\n  name\n  __typename\n}\n\nfragment TftNeedPremiumErrorFragment on TftNeedPremiumError {\n  message\n  userId\n  __typename\n}\n"
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code == 200:
        data = response.json()
        print("200 profile Request successful!")
        with open(file_name, "w") as f:
            json.dump(data, f)
    else:
        print(f"Request failed with status code: {response.status_code}")

    return data

def get_match_data(match_id,riotname,tag,region="TH"):
    
    file_name = f"output/v2-match-data-{match_id}-{region}-{riotname}-{tag}.json"
    url = "https://mobalytics.gg/api/tft/v1/graphql/query"

    headers = {
        "Content-Type": "application/json",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en_us",
        "cookie": "appmobaabgroup=A; appcfcountry=TH;",
        "dnt": "1",
        "origin": "https://mobalytics.gg",
        "referer": "https://mobalytics.gg/tft/profile/th/overview",
        "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
    }

    body = {
        "operationName": "TftMatchQuery",
        "query":"query TftMatchQuery($filter: TftMatchFilter!) {\n  tft {\n    matchV2(filter: $filter) {\n      ...TftMatchFragment\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment TftMatchFragment on TftMatch {\n  id: matchId\n  region\n  date\n  set\n  patch\n  queue\n  durationSeconds\n  participants {\n    ...TftMatchParticipantFragment\n    __typename\n  }\n  __typename\n}\n\nfragment TftMatchParticipantFragment on TftMatchParticipant {\n  puuid\n  region\n  set\n  profile {\n    ...TftProfileNestedFragment\n    __typename\n  }\n  placement\n  damageDealt\n  timeEliminatedSeconds\n  archetypeId\n  traits {\n    ...TftMatchRegistryTraitFragment\n    __typename\n  }\n  units {\n    ...TftMatchRegistryUnitFragment\n    __typename\n  }\n  augments {\n    ...TftMatchRegistryAugmentFragment\n    __typename\n  }\n  __typename\n}\n\nfragment TftProfileNestedFragment on TftProfile {\n  puuid\n  rank {\n    ...TftSummonerRankFragment\n    __typename\n  }\n  ...TftProfileSummonerInfoFragment\n  __typename\n}\n\nfragment TftProfileSummonerInfoFragment on TftProfile {\n  puuid\n  summonerInfo: info {\n    ...TftSummonerFragment\n    __typename\n  }\n  __typename\n}\n\nfragment TftSummonerFragment on TftSummoner {\n  puuid\n  accountId\n  summonerId\n  gameName\n  tagLine\n  region\n  profileIcon\n  level\n  __typename\n}\n\nfragment TftSummonerRankFragment on SummonerRank {\n  tier\n  division\n  __typename\n}\n\nfragment TftMatchRegistryTraitFragment on TftMatchRegistryTrait {\n  slug\n  numUnits\n  style\n  tierCurrent\n  tierTotal\n  __typename\n}\n\nfragment TftMatchRegistryUnitFragment on TftMatchRegistryUnit {\n  slug\n  tier\n  items\n  chosen\n  __typename\n}\n\nfragment TftMatchRegistryAugmentFragment on TftMatchRegistryAugment {\n  slug\n  __typename\n}\n",
        "variables": {"filter": {"region": region, "matchId": match_id}}
    }    

    response = requests.post(url, headers=headers, json=body)

    if response.status_code == 200:
        match_data = response.json()
        with open(file_name, "w") as f:
            json.dump(match_data, f)
        print("200 match Request successful!")

    else:
        print(f"Request failed with status code: {response.status_code}")

    return match_data

# Test the functions
if __name__ == "__main__":
    match_id = "42590337"
    riotname = "beggy"
    tag = "3105"
    profile_data = get_profile_data(riotname, tag)
    match_data = get_match_data(match_id,riotname, tag)
