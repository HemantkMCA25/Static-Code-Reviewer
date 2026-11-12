#include <vector>
#include <iostream>

// Sample input for the C++ analyzer: nested loops, branches, raw new/delete.
int* make_table(int n) {
    int* table = new int[n * n];
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (i == j && n > 1) {
                table[i * n + j] = 1;
            } else {
                table[i * n + j] = 0;
            }
        }
    }
    return table;
}

int main() {
    int* t = make_table(4);
    std::cout << t[0] << std::endl;
    delete[] t;
    return 0;
}
