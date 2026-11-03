#include <iostream>

int main()
{
    int value = 42;
    // A line comment is not a nested block comment.
    /* A standard block comment. */
    std::cout << value << std::endl;
    return 0;
}
