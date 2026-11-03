// positive_06.cpp
// Intent: lambda parameters all use type prefixes.
int main() {
    return [](unsigned int uiValue, long lOffset, int iScale) {
        return static_cast<int>(uiValue) + static_cast<int>(lOffset) + iScale;
    }(2U, 3L, 4);
}
