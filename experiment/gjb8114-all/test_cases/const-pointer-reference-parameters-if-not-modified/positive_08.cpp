#include <cstddef>
#include <map>
#include <string>

std::size_t count_entries(const std::map<std::string, int>& entries)
{
    return entries.size();
}
