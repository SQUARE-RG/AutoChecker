// positive_06.cpp
#include <iostream>
#include <stdexcept>

#define SAFE_EXECUTE(statement) try { statement; } catch (...) { std::cerr << "caught\n"; }

int main()
{
    SAFE_EXECUTE(throw std::runtime_error("boom"));
    std::cout << "done\n";
    return 0;
}
