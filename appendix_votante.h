/**
 * @file votante.h
 * @author Laura Vázquez Garcia y Paloma Ballester Asesio
 * @brief El proceso de votante
 * @date 2022-03-25
 *
 *
 */

#ifndef _VOTANTE_H
#define _VOTANTE_H

/**
 * @brief Esta función es la que ejecutan todos los procesos votantes. Empiezan esperando a la
 * señal SIGUSR1 para empezar. Se elige el candidato con un semaforo (el primero que le hace el
 * try_wait) luego con un segundo semaforo vamos controlando quien escribe en el fichero. El 
 * proceso candidato va verificando si se han hecho todos los votos. Cuando esten, los imprime
 * por pantalla. Esto se repite hasta que se recibe la señal SIGINT.Si hay algún error, sale 
 * con EXIT_FAILURE, si todo va bien, EXIT_SUCCESS.
 * 
 * @param n_procs int, numero de procesos votantes.
 */
void votante(int n_procs);
    

#endif