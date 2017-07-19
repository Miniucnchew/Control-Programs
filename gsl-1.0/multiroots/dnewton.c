/* multiroots/dnewton.c
 * 
 * Copyright (C) 1996, 1997, 1998, 1999, 2000 Brian Gough
 * 
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or (at
 * your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 */

#include <config.h>

#include <stddef.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <float.h>

#include <gsl/gsl_math.h>
#include <gsl/gsl_errno.h>
#include <gsl/gsl_multiroots.h>
#include <gsl/gsl_linalg.h>

/* Newton method using a finite difference approximation to the jacobian.
   The derivatives are estimated using a step size of 

   h_i = sqrt(DBL_EPSILON) * x_i 

   */

typedef struct
  {
    gsl_matrix * J;
    gsl_matrix * lu;
    gsl_permutation * permutation;
  }
dnewton_state_t;

static int dnewton_alloc (void * vstate, size_t n);
static int dnewton_set (void * vstate, gsl_multiroot_function * function, gsl_vector * x, gsl_vector * f, gsl_vector * dx);
static int dnewton_iterate (void * vstate, gsl_multiroot_function * function, gsl_vector * x, gsl_vector * f, gsl_vector * dx);
static void dnewton_free (void * vstate);

static int
dnewton_alloc (void * vstate, size_t n)
{
  dnewton_state_t * state = (dnewton_state_t *) vstate;
  gsl_permutation * p;
  gsl_matrix * m, * J;

  m = gsl_matrix_calloc (n,n);
  
  if (m == 0) 
    {
      GSL_ERROR_VAL ("failed to allocate space for lu", GSL_ENOMEM, 0);
    }

  state->lu = m ;

  p = gsl_permutation_calloc (n);

  if (p == 0)
    {
      gsl_matrix_free(m);

      GSL_ERROR_VAL ("failed to allocate space for permutation", GSL_ENOMEM, 0);
    }

  state->permutation = p ;

  J = gsl_matrix_calloc (n,n);

  if (J == 0)
    {
      gsl_permutation_free(p);
      gsl_matrix_free(m);

      GSL_ERROR_VAL ("failed to allocate space for d", GSL_ENOMEM, 0);
    }

  state->J = J;

  return GSL_SUCCESS;
}

static int
dnewton_set (void * vstate, gsl_multiroot_function * function, gsl_vector * x, gsl_vector * f, gsl_vector * dx)
{
  dnewton_state_t * state = (dnewton_state_t *) vstate;
  size_t i, n = function->n ;

  GSL_MULTIROOT_FN_EVAL (function, x, f);

  gsl_multiroot_fdjacobian (function, x, f, GSL_SQRT_DBL_EPSILON, state->J);

  for (i = 0; i < n; i++)
    {
      gsl_vector_set (dx, i, 0.0);
    }

  return GSL_SUCCESS;
}

static int
dnewton_iterate (void * vstate, gsl_multiroot_function * function, gsl_vector * x, gsl_vector * f, gsl_vector * dx)
{
  dnewton_state_t * state = (dnewton_state_t *) vstate;
  
  int signum ;

  size_t i;

  size_t n = function->n ;

  gsl_matrix_memcpy (state->lu, state->J);

  gsl_linalg_LU_decomp (state->lu, state->permutation, &signum);
  
  gsl_linalg_LU_solve (state->lu, state->permutation, f, dx);

  for (i = 0; i < n; i++)
    {
      double e = gsl_vector_get (dx, i);
      double y = gsl_vector_get (x, i);
      gsl_vector_set (dx, i, -e);
      gsl_vector_set (x, i, y - e);
    }
  
  {
    int status = GSL_MULTIROOT_FN_EVAL (function, x, f);

    if (status != GSL_SUCCESS) 
      {
        return GSL_EBADFUNC;
      }
  }
 
  gsl_multiroot_fdjacobian (function, x, f, GSL_SQRT_DBL_EPSILON, state->J);

  return GSL_SUCCESS;
}


static void
dnewton_free (void * vstate)
{
  dnewton_state_t * state = (dnewton_state_t *) vstate;

  gsl_matrix_free(state->J);
  gsl_matrix_free(state->lu);
  gsl_permutation_free(state->permutation);
}


static const gsl_multiroot_fsolver_type dnewton_type =
{"dnewton",				/* name */
 sizeof (dnewton_state_t),
 &dnewton_alloc,
 &dnewton_set,
 &dnewton_iterate,
 &dnewton_free};

const gsl_multiroot_fsolver_type  * gsl_multiroot_fsolver_dnewton = &dnewton_type;