/// @author Jakub Semric
/// 2018

#include <iostream>
#include <ostream>
#include <vector>
#include <ctype.h>

#include "nfa_error.hpp"
#include "nfa.hpp"
#include "pcap_reader.hpp"

namespace reduction
{

vector<pair<string,ErrorStats>> compute_error(
    const FastNfa &target, const FastNfa &reduced, const vector<string> &pcaps,
    bool consistent)
{
    for (auto i : pcaps)
    {
        char err_buf[4096] = "";
        pcap_t *p;

        if (!(p = pcap_open_offline(i.c_str(), err_buf)))
        {
            throw runtime_error("Not a valid pcap file: \'" + i + "'");
        }
        pcap_close(p);
    }

    auto fidx_target = target.get_final_state_idx();
    auto fidx_reduced = reduced.get_final_state_idx();
    vector<pair<string,ErrorStats>> results;

    for (auto p : pcaps) {
        ErrorStats stats(reduced.state_count(), target.state_count());
        try
        {
            pcapreader::process_payload(
                p.c_str(),
                [&] (const unsigned char *payload, unsigned len)
                {
                    // bit vector of reached states
                    // 0 - not reached, 1 - reached
                    vector<bool> bm(reduced.state_count());
                    reduced.parse_word(
                        payload, len, [&bm](State s){ bm[s] = 1; });

                    int match1 = 0;
                    stats.total++;
                    for (size_t i = 0; i < fidx_reduced.size(); i++)
                    {
                        size_t idx = fidx_reduced[i];
                        if (bm[idx])
                        {
                            match1++;
                            assert(idx < stats.reduced_states_arr.size());
                            stats.reduced_states_arr[idx]++;
                        }
                    }

                    //stats. += match1 > 0;
                    int match2 = 0;
                    if (match1 || consistent)
                    {    
                        // something was matched, lets find the difference
                        vector<bool> bm(target.state_count());
                        target.parse_word(
                            payload, len, [&bm](State s){ bm[s] = 1; });
                        for (size_t i = 0; i < fidx_target.size(); i++)
                        {
                            size_t idx = fidx_target[i];
                            if (bm[idx])
                            {
                                match2++;
                                assert(idx < stats.target_states_arr.size());
                                stats.target_states_arr[idx]++;
                            }
                        }

                        if (match1 != match2)
                        {
                            stats.fp_c++;
                            stats.all_c += match1 - match2;
                            if (consistent && match2 > match1)
                            {
                                throw runtime_error(
                                    "Reduced automaton ain't "
                                    "over-approximation!\n");
                            }
                        }
                        else
                        {
                            stats.pp_c++;
                        }
                        // accepted packet false/positive positive
                        if (match2) stats.pp_a++; else stats.fp_a++;
                    }
                });
            results.push_back(pair<string,ErrorStats>(p,stats));
        }
        catch (exception &e) {
            // other error
            cerr << "\033[1;31mERROR\033[0m " << e.what() << "\n";
            break;
        }
    }
    return results;
}
}