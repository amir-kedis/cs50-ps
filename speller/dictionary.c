// Implements a dictionary's functionality

#include <ctype.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>

#include "dictionary.h"

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
} node;

// TODO: Choose number of buckets in hash table
const unsigned int N = 26 * 26;

// Hash table
node *table[N];

// Returns true if word is in dictionary, else false
bool check(const char *word)
{
    // hash value
    int hValue = hash(word);
    // printf("\n%i\n", hValue);

    // loop into nodes
    for (node *cursor = table[hValue]; cursor != NULL; cursor = cursor->next)
    {
        if (strcasecmp(cursor->word, word) == 0)
        {
            return true;
        }
    }

    return false;
}

// Hashes word to a number
unsigned int hash(const char *word)
{
    // TODO: Improve this hash function
    // indecies
    int I1 = toupper(word[0]) - 'A';
    int I2 = 0;
    if (strlen(word) > 2)
    {
        I2 = toupper(word[1]) - 'A';
    }

    return (26 * (I1) + I2) % N;
}

// size counter
int size_counter = 0;

// Loads dictionary into memory, returning true if successful, else false
bool load(const char *dictionary)
{
    // open dictionary
    FILE *dict = fopen(dictionary, "r");
    if (dict == NULL)
    {
        return false;
    }

    // read strings from a file one at a time
    char word[LENGTH + 1];

    while (fscanf(dict, "%s", word) != EOF)
    {

        // create a new node for each word
        node *n = malloc(sizeof(node));
        strcpy(n->word, word);

        // hash word to obtain hash value
        unsigned int index = hash(word);

        // insert node into hash table
        n->next = table[index];
        table[index] = n;

        // increamnet word count
        size_counter++;
    }

    fclose(dict);
    return true;
}

// Returns number of words in dictionary if loaded, else 0 if not yet loaded
unsigned int size(void)
{
    return size_counter;
}

// Unloads dictionary from memory, returning true if successful, else false
bool unload(void)
{
    for (int i = 0; i <= N; i++)
    {
        while (table[i] != NULL)
        {
            node *tmp = table[i]->next;
            free(table[i]);
            table[i] = tmp;
        }
    }

    return true;
}
